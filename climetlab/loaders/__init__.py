# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import datetime
import logging
import os
import time
import warnings

import numpy as np

import climetlab as cml
from climetlab.core.order import build_remapping  # noqa:F401
from climetlab.utils import progress_bar
from climetlab.utils.config import LoadersConfig
from climetlab.utils.humanize import bytes, seconds

LOG = logging.getLogger(__name__)

VERSION = "0.7"


def get_versions():
    dic = {}

    import climetlab

    dic["climetlab"] = climetlab.__version__

    import earthkit.meteo

    dic["earthkit.meteo"] = earthkit.meteo.__version__

    return dic


def check_data_values(arr, *, name: str, log=[]):
    if name == ["lsm", "insolation"]:  # 0. to 1.
        min, max = arr.min(), arr.max()
        assert max <= 1, (name, min, max, *log)
        assert min >= 0, (name, min, max, *log)

    if name == "2t":
        min, max = arr.min(), arr.max()
        assert max <= 373.15, (name, min, max, *log)
        assert min >= 173.15, (name, min, max, *log)


def check_stats(minimum, maximum, mean, msg, **kwargs):
    tolerance = (abs(minimum) + abs(maximum)) * 0.01
    if (mean - minimum < -tolerance) or (mean - minimum < -tolerance):
        raise ValueError(
            f"Mean is not in min/max interval{msg} : we should have {minimum} <= {mean} <= {maximum}"
        )


def _prepare_serialisation(o):
    if isinstance(o, dict):
        dic = {}
        for k, v in o.items():
            v = _prepare_serialisation(v)
            if k == "order_by":
                # zarr attributes are saved with sort_keys=True
                # and ordered dict are reordered.
                # This is a problem for "order_by"
                # We ensure here that the order_by key contains
                # a list of dict
                v = [{kk: vv} for kk, vv in v.items()]
            dic[k] = v
        return dic

    if isinstance(o, (list, tuple)):
        return [_prepare_serialisation(v) for v in o]

    if o in (None, True, False):
        return o

    if isinstance(o, (str, int, float)):
        return o

    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

    return str(o)


class OffsetView:
    def __init__(self, large_array, *, offset, axis, shape):
        """
        A view on a portion of the large_array.
        'axis' is the axis along which the offset applies.
        'shape' is the shape of the view.
        """
        self.large_array = large_array
        self.offset = offset
        self.axis = axis
        self.shape = shape

    def __setitem__(self, key, values):
        if isinstance(key, slice):
            # Ensure that the slice covers the entire view along the axis.
            assert key.start is None and key.stop is None, key

            # Create a new key for indexing the large array.
            new_key = tuple(
                slice(self.offset, self.offset + values.shape[i])
                if i == self.axis
                else slice(None)
                for i in range(len(self.shape))
            )
        else:
            # For non-slice keys, adjust the key based on the offset and axis.
            new_key = tuple(
                k + self.offset if i == self.axis else k for i, k in enumerate(key)
            )
        self.large_array[new_key] = values


class LoopItemsFilter:
    def __init__(self, *, loader, parts, **kwargs):
        self.loader = loader

        if parts is None:
            self.parts = None
            return

        if len(parts) == 1:
            part = parts[0]
            if part.lower() in ["all", "*"]:
                self.parts = None
                return

            if "/" in part:
                i_chunk, n_chunks = part.split("/")
                i_chunk, n_chunks = int(i_chunk), int(n_chunks)

                total = len(self.loader.registry.get_flags())
                assert i_chunk > 0, f"Chunk number {i_chunk} must be positive."
                if n_chunks > total:
                    warnings.warn(
                        f"Number of chunks {n_chunks} is larger than the total number of chunks: {total}+1."
                    )

                chunk_size = total / n_chunks
                parts = [
                    x
                    for x in range(total)
                    if x >= (i_chunk - 1) * chunk_size and x < i_chunk * chunk_size
                ]

        parts = [int(_) for _ in parts]
        print(f"Running parts: {parts}")
        if not parts:
            warnings.warn(f"Nothing to do for chunk {i_chunk}.")

        self.parts = parts

    def __call__(self, iloop, vars):
        if self.parts is None:
            return True
        # iloop index starts at 0
        # self.parts is a list of indices starting at 1
        return iloop in self.parts


class Loader:
    def __init__(self, *, path, config, print=print, **kwargs):
        self.main_config = LoadersConfig(config)
        self.path = path
        self.kwargs = kwargs
        self.print = print
        self.registry = ZarrBuiltRegistry(self.path)

    def load(self, **kwargs):
        import zarr

        self.z = zarr.open(self.path, mode="r+")
        self.registry.add_to_history("loading_data_start", parts=kwargs.get("parts"))

        filter = LoopItemsFilter(loader=self, **kwargs)
        nloop = len(list((self.iter_loops())))
        for iloop, vars in enumerate(self.iter_loops()):
            if not filter(iloop, vars):
                continue
            if self.registry.get_flag(iloop):
                print(f" -> Skipping {iloop} total={nloop} (already done)")
                continue
            self.print(f" -> Processing i={iloop=} total={nloop}")

            config = self.main_config.substitute(vars)
            cube = self.config_to_data_cube(config)

            shape = cube.extended_user_shape
            chunks = cube.chunking(config.output.chunking)
            axis = config.output.append_axis

            slice = self.registry.get_slice_for(iloop)
            print(f"Building to ZARR '{self.path}':")
            self.print(f"Building ZARR (total shape ={shape}) at {slice}, {chunks=}")

            offset = slice.start
            array = OffsetView(self.z["data"], offset=offset, axis=axis, shape=shape)

            self.load_datacube(cube, array)

            self.registry.set_flag(iloop)

        self.registry.add_to_history("loading_data_end", parts=kwargs.get("parts"))

    def load_datacube(self, cube, array):
        start = time.time()
        load = 0
        save = 0

        reading_chunks = None
        total = cube.count(reading_chunks)
        for i, cubelet in enumerate(
            progress_bar(
                iterable=cube.iterate_cubelets(reading_chunks),
                total=total,
            )
        ):
            now = time.time()
            data = cubelet.to_numpy()
            load += time.time() - now

            j = cubelet.extended_icoords[1]
            check_data_values(
                data[:],
                name=self._variables_names[j],
                log=[i, j, data.shape, cubelet.extended_icoords],
            )

            now = time.time()
            array[cubelet.extended_icoords] = data
            save += time.time() - now

        now = time.time()
        save += time.time() - now

        print("Written")
        self.print_info()
        print("Written.")

        self.print(
            f"Elapsed: {seconds(time.time() - start)},"
            f" load time: {seconds(load)},"
            f" write time: {seconds(save)}."
        )


def add_zarr_dataset(name, nparray, *, zarr_root, overwrite=True, dtype=np.float32):
    if isinstance(nparray, (tuple, list)):
        nparray = np.array(nparray, dtype=dtype)
    a = zarr_root.create_dataset(
        name,
        shape=nparray.shape,
        dtype=dtype,
        overwrite=overwrite,
    )
    a[...] = nparray[...]
    return a


class ZarrBuiltRegistry:
    name_lengths = "_build_lengths"
    name_flags = "_build_flags"
    lengths = None
    flags = None
    z = None

    def __init__(self, path):
        import zarr

        assert isinstance(path, str), path
        self.zarr_path = path
        self.synchronizer = zarr.ProcessSynchronizer(
            os.path.join(self.zarr_path, "registry.sync")
        )

    def get_slice_for(self, iloop):
        lengths = self.get_lengths()
        assert iloop >= 0 and iloop < len(lengths)
        start = sum(lengths[:iloop])
        stop = sum(lengths[: (iloop + 1)])
        return slice(start, stop)

    def get_lengths(self):
        z = self._open_read()
        return list(z[self.name_lengths][:])

    def get_flags(self, **kwargs):
        z = self._open_read(**kwargs)
        print(list(z[self.name_flags][:]))
        return list(z[self.name_flags][:])

    def get_flag(self, iloop):
        z = self._open_read()
        return z[self.name_flags][iloop]

    def set_flag(self, iloop, value=True):
        z = self._open_write()
        z.attrs["latest_write_timestamp"] = datetime.datetime.utcnow().isoformat()
        z[self.name_flags][iloop] = value

    def _open_read(self, sync=True):
        import zarr

        if sync:
            return zarr.open(self.zarr_path, mode="r", synchronizer=self.synchronizer)
        else:
            return zarr.open(self.zarr_path, mode="r")

    def _open_write(self):
        import zarr

        return zarr.open(self.zarr_path, mode="r+", synchronizer=self.synchronizer)

    def create(self, lengths, overwrite=False):
        z = self._open_write()

        add_zarr_dataset(
            self.name_lengths,
            lengths,
            zarr_root=z,
            dtype="i4",
            overwrite=overwrite,
        )
        add_zarr_dataset(
            self.name_flags,
            len(lengths) * [False],
            zarr_root=z,
            dtype=bool,
            overwrite=overwrite,
        )
        z = None
        self.add_to_history("initialised")

    def reset(self, lengths):
        return self.create(lengths, overwrite=True)

    def add_to_history(self, action, **kwargs):
        new = dict(
            action=action,
            timestamp=datetime.datetime.utcnow().isoformat(),
            versions=get_versions(),
        )
        new.update(kwargs)

        z = self._open_write()
        history = z.attrs.get("history", [])
        history.append(new)
        z.attrs["history"] = history


class ZarrLoader(Loader):
    writer = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.z = None
        self.statistics = []

    @classmethod
    def from_config(cls, *, config, path, **kwargs):
        # config is the path to the config file
        # or a dict with the config
        obj = cls(config=config, path=path, **kwargs)
        return obj

    @classmethod
    def from_zarr(cls, *, config, path, **kwargs):
        import zarr

        assert os.path.exists(path), path
        z = zarr.open(path, mode="r")
        config = z.attrs["create_yaml_config"]
        # config = yaml.safe_load(z.attrs["_yaml_dump"])["create_yaml_config"]
        kwargs.get("print", print)("Config loaded from zarr: ", config)
        return cls.from_config(config=config, path=path, **kwargs)

    def iter_loops(self):
        if "loop" not in self.main_config or self.main_config.loop is None:
            raise NotImplementedError()
            yield None  # ?
            return

        for vars in self.main_config._iter_loops():
            yield vars

    def _compute_lengths(self, multiply):
        def squeeze_dict(dic):
            keys = list(dic.keys())
            assert len(dic) == 1, keys
            return dic[keys[0]]

        lengths = []
        for i, vars in enumerate(self.iter_loops()):
            lst = squeeze_dict(vars)
            assert isinstance(lst, (tuple, list)), lst
            lengths.append(len(lst))

        lengths = [x * multiply for x in lengths]
        return lengths

    @property
    def _variables_names(self):
        return self.main_config.output.order_by[self.main_config.output.statistics]

    def initialise(self):
        """Create empty zarr from self.main_config and self.path"""
        import pandas as pd
        import zarr

        from climetlab.utils.dates import to_datetime  # avoid circular imports

        variables = self._variables_names

        def get_first_and_last_element_configs():
            first = None
            for i, vars in enumerate(self.iter_loops()):
                keys = list(vars.keys())
                assert len(vars) == 1, keys
                key = keys[0]
                if first is None:
                    first = self.main_config.substitute({key: vars[key][0]})
            last = self.main_config.substitute({key: vars[key][-1]})
            return first, last

        first, last = get_first_and_last_element_configs()

        first_cube, grid_points = self.config_to_data_cube(first, with_gridpoints=True)
        last_cube, grid_points_ = self.config_to_data_cube(last, with_gridpoints=True)
        for _ in zip(grid_points, grid_points_):
            assert (_[0] == _[1]).all(), (grid_points_, grid_points)

        assert first_cube.extended_user_shape[1] == len(variables), (
            first_cube.extended_user_shape,
            len(variables),
        )
        assert last_cube.extended_user_shape[1] == len(variables), (
            last_cube.extended_user_shape,
            len(variables),
        )

        shape = list(first_cube.extended_user_shape)
        assert shape == list(last_cube.extended_user_shape), (
            shape,
            list(last_cube.extended_user_shape),
        )
        # Notice that shape[0] can be >1
        # we are assuming that all data has the same shape
        one_element_length = shape[0]
        lengths = self._compute_lengths(one_element_length)

        total_shape = [sum(lengths), *shape[1:]]

        chunks = first_cube.chunking(self.main_config.output.chunking)
        dtype = self.main_config.output.dtype

        self.print(
            f"Creating ZARR '{self.path}', with {total_shape=}, "
            f"{chunks=} and {dtype=}"
        )

        resolution = first_cube.source[0].resolution

        first_date = to_datetime(first_cube.user_coords["valid_datetime"][0])
        last_date = to_datetime(last_cube.user_coords["valid_datetime"][-1])
        frequency = (
            (last_date - first_date).total_seconds() / 3600 / (total_shape[0] - 1)
        )
        if int(frequency) != frequency:
            raise ValueError(
                (
                    "Cannot compute frequency. Data is not regularly organised ? "
                    f"{first_date=}; {last_date=}; {total_shape[0]=}; {frequency=}"
                )
            )
        frequency = int(frequency)

        def check(name, resolution, first_date, last_date, frequency):
            resolution_str = str(resolution).replace(".", "p").lower()
            if f"-{resolution_str}-" not in name:
                msg = (
                    f"Resolution {resolution_str} should appear in the dataset name ({name})."
                    " Use --no-check to ignore."
                )
                self.print(msg)
                raise ValueError(msg)

            if f"-{frequency}h-" not in name:
                msg = f"Frequency {frequency}h should appear in the dataset name ({name}). Use --no-check to ignore."
                self.print(msg)
                raise ValueError(msg)

            if f"-{first_date.year}-" not in name:
                msg = f"Year {first_date.year} should appear in the dataset name ({name}). Use --no-check to ignore."
                self.print(msg)
                raise ValueError(msg)

            if f"-{last_date.year}-" not in name:
                msg = f"Year {last_date.year} should appear in the dataset name ({name}). Use --no-check to ignore."
                self.print(msg)
                raise ValueError(msg)

        if not self.kwargs["no_check"]:
            check(
                os.path.basename(self.path),
                resolution,
                first_date,
                last_date,
                frequency,
            )

        metadata = {}

        metadata.update(self.main_config.get("add_metadata", {}))

        metadata["create_yaml_config"] = _prepare_serialisation(self.main_config)

        metadata["resolution"] = resolution

        metadata["variables"] = self._variables_names

        metadata["version"] = VERSION

        metadata["frequency"] = frequency
        metadata["first_date"] = first_date.isoformat()
        metadata["last_date"] = last_date.isoformat()
        pd_dates = pd.date_range(
            start=metadata["first_date"],
            end=metadata["last_date"],
            freq=f"{metadata['frequency']}h",
            unit="s",
        )
        assert pd_dates.size == total_shape[0], (pd_dates, total_shape)
        assert pd_dates[-1] == last_date, (pd_dates, last_date)

        # metadata["_yaml_dump"] = yaml.dump(metadata, sort_keys=False)
        metadata.update(self.main_config.get("force_metadata", {}))

        # write data
        self.z = zarr.open(self.path, mode="w")

        self.z.create_dataset("data", shape=total_shape, chunks=chunks, dtype=dtype)

        np_dates = pd_dates.to_numpy()
        self._add_dataset("dates", np_dates, dtype=np_dates.dtype)

        assert grid_points[0].shape == grid_points[1].shape
        self._add_dataset("latitudes", grid_points[0])
        self._add_dataset("longitudes", grid_points[1])

        # write metadata
        for k, v in metadata.items():
            print(v)
            self.z.attrs[k] = v

        self.z = None

        self.registry.create(lengths=lengths)

    def config_to_data_cube(self, config, with_gridpoints=False):
        start = time.time()
        data = cml.load_source("loader", config.input)
        assert len(data), f"No data for {config}"
        self.print(f"Done in {seconds(time.time()-start)}, length: {len(data):,}.")

        start = time.time()
        self.print("Sorting dataset")
        cube = data.cube(
            config.output.order_by,
            remapping=config.output.remapping,
            flatten_values=config.output.flatten_values,
        )
        cube = cube.squeeze()
        self.print(f"Sorting done in {seconds(time.time()-start)}.")

        if not with_gridpoints:
            return cube
        else:
            return cube, data[0].grid_points()

    def _add_dataset(self, *args, **kwargs):
        import zarr

        z = self.z
        if z is None:
            z = zarr.open(self.path, mode="r+")

        return add_zarr_dataset(*args, **kwargs, zarr_root=z)

    def print_info(self):
        assert self.z is not None
        try:
            print(self.z["data"].info)
        except Exception as e:
            print(e)
        print("...")
        try:
            print(self.z["data"].info)
        except Exception as e:
            print(e)

    def add_statistics(self, statistics_start, statistics_end, no_write, **kwargs):
        do_write = not no_write

        incomplete = not all(self.registry.get_flags(sync=False))
        if do_write and incomplete:
            raise Exception(
                f"Zarr {self.path} is not fully built, not writing statistics."
            )

        if statistics_start is None:
            statistics_start = self.main_config.output.get("statistics_start")
        if statistics_end is None:
            statistics_end = self.main_config.output.get("statistics_end")

        if do_write:
            self.registry.add_to_history(
                "compute_statistics_start",
                start=statistics_start,
                end=statistics_end,
            )

        try:
            from ecml_tools.data import open_dataset
        except ImportError:
            raise Exception("Need to pip install ecml_tools")
        ds = open_dataset(self.path)

        stats = self.compute_statistics(ds, statistics_start, statistics_end)

        print(
            "\n".join(
                (
                    f"{v.rjust(10)}: "
                    f"min/max = {stats['minimum'][j]:.6g} {stats['maximum'][j]:.6g}"
                    "   \t:   "
                    f"mean/stdev = {stats['mean'][j]:.6g} {stats['stdev'][j]:.6g}"
                )
                for j, v in enumerate(ds.variables)
            )
        )

        if do_write:
            for k in [
                "mean",
                "stdev",
                "minimum",
                "maximum",
                "sums",
                "squares",
                "count",
            ]:
                self._add_dataset(k, stats[k])

            self.registry.add_to_history(
                "compute_statistics_end",
                start=statistics_start,
                end=statistics_end,
            )

    def compute_statistics(self, ds, statistics_start, statistics_end):
        import zarr

        data = zarr.open(self.path, mode="r")["data"]

        shape = data.shape
        assert shape[0] == len(ds.dates)
        assert shape[1] == len(ds.variables)
        assert ds.variables == self._variables_names

        subset = ds._dates_to_indices(start=statistics_start, end=statistics_end)

        self.print(
            f"Statistics computed on {len(subset)}/{shape[0]} samples "
            f"first={ds.dates[subset[0]]} "
            f"last={ds.dates[subset[-1]]}"
        )
        if not subset:
            raise ValueError(
                f"Cannot compute statistics on an empty interval."
                f" Requested : {statistics_start=} {statistics_end=}."
                f" Available: {ds.dates[0]=} {ds.dates[-1]=}"
            )

        stats_shape = (len(subset), shape[1])

        mean = np.zeros(shape=stats_shape)
        stdev = np.zeros(shape=stats_shape)
        minimum = np.zeros(shape=stats_shape)
        maximum = np.zeros(shape=stats_shape)
        sums = np.zeros(shape=stats_shape)
        squares = np.zeros(shape=stats_shape)
        count = np.zeros(shape=stats_shape)

        for i, i_data in enumerate(subset):
            chunk = data[i_data, ...]
            self.print(
                f"Computing statistics on {i_data+1}/{shape[0]} ({ds.dates[i_data]})"
            )
            for j in range(shape[1]):
                values = chunk[j, :]
                check_data_values(
                    values,
                    name=ds.variables[j],
                    log=[j, i, i_data, "statistics"],
                )
                minimum[i, j] = np.amin(values)
                maximum[i, j] = np.amax(values)
                sums[i, j] = np.sum(values)
                squares[i, j] = np.sum(values * values)
                count[i, j] = values.size
                mean[i, j] = sums[i, j] / count[i, j]
                stdev[i, j] = np.sqrt(
                    squares[i, j] / count[i, j] - mean[i, j] * mean[i, j]
                )

                check_stats(
                    minimum=minimum[i, j],
                    maximum=maximum[i, j],
                    mean=mean[i, j],
                    msg=f" for {j} {ds.variables[j]}",
                )

        assert (count == count[:][0]).all(), count

        assert len(minimum.shape) == 2
        assert minimum.shape[0] == len(subset)
        assert minimum.shape[1] == shape[1]

        _minimum = np.amin(minimum, axis=0)
        _maximum = np.amax(maximum, axis=0)
        _count = np.sum(count, axis=0)
        _sums = np.sum(sums, axis=0)
        _squares = np.sum(squares, axis=0)
        _mean = _sums / _count
        _stdev = np.sqrt(_squares / _count - _mean * _mean)

        stats = {
            "mean": _mean,
            "stdev": _stdev,
            "minimum": _minimum,
            "maximum": _maximum,
            "sums": _sums,
            "squares": _squares,
            "count": _count,
        }

        for v in stats.values():
            assert v.shape == stats["mean"].shape

        for i, name in enumerate(ds.variables):
            check_stats(**{k: v[i] for k, v in stats.items()}, msg=f"{i} {name}")

        return stats


class HDF5Loader:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

    def append_array(self, *args, **kwargs):
        raise NotImplementedError("Appending do HDF5 not yet implemented")

    def create_array(
        self,
        dataset,
        shape,
        chunks,
        dtype,
        metadata,
        grid_points,
        nloops,
    ):
        import h5py

        if not isinstance(chunks, tuple):
            chunks = None

        print(
            f"Creating HDD5 file '{self.path}', with {dataset=}, {shape=}, {chunks=} and {dtype=}"
        )

        self.h5 = h5py.File(self.path, mode="w")
        array = self.h5.create_dataset(
            dataset,
            chunks=chunks,
            maxshape=shape,
            dtype=dtype,
            data=np.empty(
                shape
            )  # Can we avoid that? Looks like its needed for chuncking
            # data = h5py.Empty(dtype),
        )
        return array

    def close(self):
        self.h5.close()
        del self.h5

    def print_info(self):
        import h5py

        def h5_tree(h5, depth=0):
            for k, v in h5.items():
                if isinstance(v, h5py._hl.group.Group):
                    h5_tree(v, depth + 1)
                else:
                    print(" " * (depth * 3), k, v)
                    for p, q in v.attrs.items():
                        print(" " * (depth * 3 + 3), p, q)

        size = os.path.getsize(self.path)
        print(f"HDF5 file {self.path}: {size:,} ({bytes(size)})")
        with h5py.File(self.path, mode="r") as f:
            print("Content:")
            h5_tree(f, 1)
