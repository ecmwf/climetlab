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
import re
import time
import uuid
import warnings
from functools import cached_property

import numpy as np

from climetlab.core.order import build_remapping  # noqa:F401
from climetlab.utils import progress_bar
from climetlab.utils.config import LoadersConfig
from climetlab.utils.humanize import bytes, seconds


class DatasetName:
    def __init__(
        self,
        name,
        resolution=None,
        start_date=None,
        end_date=None,
        frequency=None,
    ):
        self.name = name
        self.parsed = self._parse(name)

        self.messages = []

        self.check_parsed()
        self.check_resolution(resolution)
        self.check_frequency(frequency)
        self.check_start_date(start_date)
        self.check_end_date(end_date)

        if self.messages:
            self.messages.append(
                f"{self} is parsed as :"
                + "/".join(f"{k}={v}" for k, v in self.parsed.items())
            )

    @property
    def is_valid(self):
        return not self.messages

    @property
    def error_message(self):
        out = " And ".join(self.messages)
        if out:
            out = out[0].upper() + out[1:]
        return out

    def raise_if_not_valid(self, print=print):
        if not self.is_valid:
            for m in self.messages:
                print(m)
            raise ValueError(self.error_message)

    def _parse(self, name):
        pattern = r"^(\w+)-(\w+)-(\w+)-(\w+)-(\w\w\w\w)-(\w+)-(\w+)-([\d\-]+)-(\d+h)-v(\d+)-?(.*)$"
        match = re.match(pattern, name)

        parsed = {}
        if match:
            keys = [
                "use_case",
                "class_",
                "type_",
                "stream",
                "expver",
                "source",
                "resolution",
                "period",
                "frequency",
                "version",
                "additional",
            ]
            parsed = {k: v for k, v in zip(keys, match.groups())}

            period = parsed["period"].split("-")
            assert len(period) in (1, 2), (name, period)
            parsed["start_date"] = period[0]
            if len(period) == 1:
                parsed["end_date"] = period[0]
            if len(period) == 2:
                parsed["end_date"] = period[1]

        return parsed

    def __str__(self):
        return self.name

    def check_parsed(self):
        if not self.parsed:
            self.messages.append(
                (
                    f"the dataset name {self} does not follow naming convention. "
                    "See here for details: "
                    "https://confluence.ecmwf.int/display/DWF/Datasets+available+as+zarr"
                )
            )

    def check_resolution(self, resolution):
        if (
            self.parsed.get("resolution")
            and self.parsed["resolution"][0] not in "0123456789on"
        ):
            self.messages.append(
                (
                    f"the resolution {self.parsed['resolution'] } should start "
                    f"with a number or 'o' or 'n' in the dataset name {self}."
                )
            )

        if resolution is None:
            return
        resolution_str = str(resolution).replace(".", "p").lower()
        self._check_missing("resolution", resolution_str)
        self._check_mismatch("resolution", resolution_str)

    def check_frequency(self, frequency):
        if frequency is None:
            return
        frequency_str = f"{frequency}h"
        self._check_missing("frequency", frequency_str)
        self._check_mismatch("frequency", frequency_str)

    def check_start_date(self, start_date):
        if start_date is None:
            return
        start_date_str = str(start_date.year)
        self._check_missing("first date", start_date_str)
        self._check_mismatch("start_date", start_date_str)

    def check_end_date(self, end_date):
        if end_date is None:
            return
        end_date_str = str(end_date.year)
        self._check_missing("end_date", end_date_str)
        self._check_mismatch("end_date", end_date_str)

    def _check_missing(self, key, value):
        if value not in self.name:
            self.messages.append(
                (f"the {key} is {value}, but is missing in {self.name}.")
            )

    def _check_mismatch(self, key, value):
        if self.parsed.get(key) and self.parsed[key] != value:
            self.messages.append(
                (f"the {key} is {value}, but is {self.parsed[key]} in {self.name}.")
            )


LOG = logging.getLogger(__name__)

VERSION = "0.12"


def get_versions():
    dic = {}

    import climetlab

    dic["climetlab"] = climetlab.__version__

    import earthkit.meteo

    dic["earthkit.meteo"] = earthkit.meteo.__version__

    return dic


def check_data_values(arr, *, name: str, log=[]):
    min, max = arr.min(), arr.max()
    assert not (np.isnan(arr).any()), (name, min, max, *log)

    if min == 9999.0:
        warnings.warn(f"Min value 9999 for {name}")
    if max == 9999.0:
        warnings.warn(f"Max value 9999 for {name}")

    if name == ["lsm", "insolation"]:  # 0. to 1.
        assert max <= 1, (name, min, max, *log)
        assert min >= 0, (name, min, max, *log)

    if name == "2t":  # surface temp between -100 celcius and +100 celcius
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


class CubesFilter:
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

    def __call__(self, i):
        if self.parts is None:
            return True
        return i in self.parts


class Loader:
    def __init__(self, *, path, config, print=print, **kwargs):
        self.main_config = LoadersConfig(config)
        self.input_handler = self.main_config.input_handler()
        self.path = path
        self.kwargs = kwargs
        self.print = print
        self.registry = ZarrBuiltRegistry(self.path)

    def load(self, **kwargs):
        import zarr

        self.z = zarr.open(self.path, mode="r+")
        self.registry.add_to_history("loading_data_start", parts=kwargs.get("parts"))

        filter = CubesFilter(loader=self, **kwargs)
        ncubes = self.input_handler.n_cubes
        for icube, cubecreator in enumerate(self.input_handler.iter_cubes()):
            if not filter(icube):
                continue
            if self.registry.get_flag(icube):
                print(f" -> Skipping {icube} total={ncubes} (already done)")
                continue
            self.print(f" -> Processing i={icube=} total={ncubes}")

            cube = cubecreator.to_cube()
            shape = cube.extended_user_shape
            chunks = cube.chunking(self.input_handler.output.chunking)
            axis = self.input_handler.output.append_axis

            slice = self.registry.get_slice_for(icube)

            print(f"Building ZARR '{self.path}'")
            self.print(f"Building ZARR (total shape ={shape}) at {slice}, {chunks=}")

            offset = slice.start
            array = OffsetView(self.z["data"], offset=offset, axis=axis, shape=shape)

            self.load_datacube(cube, array)

            self.registry.set_flag(icube)

        self.registry.add_to_history("loading_data_end", parts=kwargs.get("parts"))
        self.registry.add_provenance(name="provenance_load")

    def load_datacube(self, cube, array):
        start = time.time()
        load = 0
        save = 0

        reading_chunks = None
        total = cube.count(reading_chunks)
        self.print(f"Loading datacube {cube}")
        bar = progress_bar(
            iterable=cube.iterate_cubelets(reading_chunks),
            total=total,
            desc=f"Loading datacube {cube}",
        )
        for i, cubelet in enumerate(bar):
            now = time.time()
            data = cubelet.to_numpy()
            bar.set_description(f"{i}/{total} {str(cubelet)} ({data.shape})")
            self.print(f"Loading datacube {cube}: {i}/{total}")
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

    def get_slice_for(self, i):
        lengths = self.get_lengths()
        assert i >= 0 and i < len(lengths)

        start = sum(lengths[:i])
        stop = sum(lengths[: (i + 1)])
        return slice(start, stop)

    def get_lengths(self):
        z = self._open_read()
        return list(z[self.name_lengths][:])

    def get_flags(self, **kwargs):
        z = self._open_read(**kwargs)
        print(list(z[self.name_flags][:]))
        return list(z[self.name_flags][:])

    def get_flag(self, i):
        z = self._open_read()
        return z[self.name_flags][i]

    def set_flag(self, i, value=True):
        z = self._open_write()
        z.attrs["latest_write_timestamp"] = datetime.datetime.utcnow().isoformat()
        z[self.name_flags][i] = value

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

    def add_provenance(self, name):
        from ecml_tools.provenance import gather_provenance_info

        z = self._open_write()
        z.attrs[name] = gather_provenance_info()

    def add_to_history(self, action, **kwargs):
        new = dict(
            action=action,
            timestamp=datetime.datetime.utcnow().isoformat(),
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
        config = z.attrs["_create_yaml_config"]
        # config = yaml.safe_load(z.attrs["_yaml_dump"])["_create_yaml_config"]
        kwargs.get("print", print)("Config loaded from zarr: ", config)
        return cls.from_config(config=config, path=path, **kwargs)

    def iter_loops(self):
        for vars in self.input_handler.iter_loops():
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
            print("i vars", i, vars, lengths, lst, f"{multiply=}")

        lengths = [x * multiply for x in lengths]
        return lengths

    @property
    def _variables_names(self):
        return self.main_config.output.order_by[self.main_config.output.statistics]

    def initialise(self):
        """Create empty zarr from self.main_config and self.path"""
        import pandas as pd
        import zarr

        self.print("config loaded ok:")
        print(self.main_config)
        print("-------------------------")

        total_shape = self.input_handler.shape
        self.print(f"total_shape = {total_shape}")
        print("-------------------------")

        grid_points = self.input_handler.grid_points
        print(f"gridpoints size: {[len(i) for i in grid_points]}")
        print("-------------------------")

        dates = self.input_handler.get_datetimes()
        self.print(f"Found {len(dates)} datetimes.")
        print(
            f"Dates: Found {len(dates)} datetimes, in {self.input_handler.n_cubes} cubes: ",
            end="",
        )
        lengths = [str(len(c.get_datetimes())) for c in self.input_handler.iter_cubes()]
        print("+".join(lengths))
        self.print(f"Found {len(dates)} datetimes {'+'.join(lengths)}.")
        print("-------------------------")

        variables_names = self.input_handler.variables

        assert (
            variables_names
            == self.main_config.output.order_by[self.main_config.output.statistics]
        ), (
            f"Requested= {self.main_config.output.order_by[self.main_config.output.statistics]} "
            f"Actual= {variables_names}"
        )

        resolution = self.input_handler.resolution

        chunks = self.input_handler.chunking
        dtype = self.main_config.output.dtype

        self.print(
            f"Creating ZARR '{self.path}', with {total_shape=}, "
            f"{chunks=} and {dtype=}"
        )

        frequency = self.input_handler.frequency
        assert isinstance(frequency, int), frequency

        if not self.kwargs["no_check"]:
            basename, ext = os.path.splitext(os.path.basename(self.path))

            ds_name = DatasetName(
                basename,
                resolution,
                dates[0],
                dates[-1],
                frequency,
            )
            ds_name.raise_if_not_valid(print=self.print)

        metadata = {}
        metadata["uuid"] = str(uuid.uuid4())

        metadata.update(self.main_config.get("add_metadata", {}))

        metadata["_create_yaml_config"] = _prepare_serialisation(self.main_config)

        metadata["description"] = self.main_config.description
        metadata["resolution"] = resolution

        metadata["data_request"] = self.input_handler.data_request

        metadata["order_by"] = self.main_config.output.order_by
        metadata["remapping"] = self.main_config.output.remapping
        metadata["flatten_grid"] = self.main_config.output.flatten_grid
        metadata["ensemble_dimension"] = self.main_config.output.ensemble_dimension

        metadata["variables"] = variables_names
        metadata["version"] = VERSION
        metadata["frequency"] = frequency
        metadata["start_date"] = dates[0].isoformat()
        metadata["end_date"] = dates[-1].isoformat()
        pd_dates_kwargs = dict(
            start=metadata["start_date"],
            end=metadata["end_date"],
            freq=f"{metadata['frequency']}h",
            unit="s",
        )
        pd_dates = pd.date_range(**pd_dates_kwargs)

        def check_dates(input_handler, pd_dates, total_shape):
            for i, loop in enumerate(input_handler.loops):
                print(f"Loop {i}: ", loop._info)
            if pd_dates.size != total_shape[0]:
                raise ValueError(
                    f"Final date size {pd_dates.size} (from {pd_dates[0]} to {pd_dates[-1]}, "
                    f"{frequency=}) does not match data shape {total_shape[0]}. {total_shape=}"
                )
            if pd_dates.size != len(dates):
                raise ValueError(
                    f"Final date size {pd_dates.size} (from {pd_dates[0]} to {pd_dates[-1]}, "
                    f"{frequency=}) does not match data shape {len(dates)} (from {dates[0]} to "
                    f"{dates[-1]}). {pd_dates_kwargs}"
                )

        check_dates(self.input_handler, pd_dates, total_shape)

        metadata.update(self.main_config.get("force_metadata", {}))

        # write data
        self.z = zarr.open(self.path, mode="w")

        self.z.create_dataset("data", shape=total_shape, chunks=chunks, dtype=dtype)

        np_dates = pd_dates.to_numpy()
        self._add_dataset("dates", np_dates, dtype=np_dates.dtype)

        self._add_dataset("latitudes", grid_points[0])
        self._add_dataset("longitudes", grid_points[1])

        self.z = None

        self.update_metadata(**metadata)

        self.registry.create(lengths=lengths)

        self.registry.add_to_history("init finished")

    def update_metadata(self, **kwargs):
        import zarr

        z = zarr.open(self.path, mode="w+")
        for k, v in kwargs.items():
            if isinstance(v, np.datetime64):
                v = v.astype(datetime.datetime)
            if isinstance(v, datetime.date):
                v = v.isoformat()
            z.attrs[k] = v

    def statistics_start_indice(self):
        return self._statistics_subset_indices[0]

    def statistics_end_indice(self):
        return self._statistics_subset_indices[1]

    def _actual_statistics_start(self):
        return self._statistics_subset_indices[2]

    def _actual_statistics_end(self):
        return self._statistics_subset_indices[3]

    @cached_property
    def _statistics_subset_indices(self):
        statistics_start = self.main_config.output.get("statistics_start")
        statistics_end = self.main_config.output.get("statistics_end")
        try:
            from ecml_tools.data import open_dataset
        except ImportError:
            raise Exception("Need to pip install ecml_tools[zarr]")

        if statistics_end is None:
            warnings.warn(
                "No statistics_end specified, using last date of the dataset."
            )
        ds = open_dataset(self.path)
        subset = ds.dates_interval_to_indices(statistics_start, statistics_end)

        return (subset[0], subset[-1], ds.dates[subset[0]], ds.dates[subset[-1]])

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

    def add_statistics(self, no_write, **kwargs):
        do_write = not no_write

        incomplete = not all(self.registry.get_flags(sync=False))
        if do_write and incomplete:
            raise Exception(
                f"Zarr {self.path} is not fully built, not writing statistics."
            )

        statistics_start = self.main_config.output.get("statistics_start")
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

            self.update_metadata(
                statistics_start_date=self._actual_statistics_start(),
                statistics_end_date=self._actual_statistics_end(),
            )

            self.registry.add_to_history(
                "compute_statistics_end",
                start=statistics_start,
                end=statistics_end,
            )
            self.registry.add_provenance(name="provenance_statistics")

    def compute_statistics(self, ds, statistics_start, statistics_end):
        import zarr

        data = zarr.open(self.path, mode="r")["data"]

        shape = data.shape
        assert shape[0] == len(ds.dates)
        assert shape[1] == len(ds.variables)
        assert ds.variables == self._variables_names

        i_start = self.statistics_start_indice()
        i_end = self.statistics_end_indice()

        i_len = i_end + 1 - i_start

        self.print(
            f"Statistics computed on {i_len}/{shape[0]} samples "
            f"first={ds.dates[i_start]} "
            f"last={ds.dates[i_end]}"
        )
        if i_end < i_start:
            raise ValueError(
                f"Cannot compute statistics on an empty interval."
                f" Requested : {ds.dates[i_start]} {ds.dates[i_end]}."
                f" Available: {ds.dates[0]=} {ds.dates[-1]=}"
            )

        stats_shape = (i_len, shape[1])

        mean = np.zeros(shape=stats_shape)
        stdev = np.zeros(shape=stats_shape)
        minimum = np.zeros(shape=stats_shape)
        maximum = np.zeros(shape=stats_shape)
        sums = np.zeros(shape=stats_shape)
        squares = np.zeros(shape=stats_shape)
        count = np.zeros(shape=stats_shape)

        for i, i_data in enumerate(range(i_start, i_end + 1)):
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
        assert minimum.shape[0] == i_len
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
