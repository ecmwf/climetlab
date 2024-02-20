# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from functools import cached_property
from itertools import product

from climetlab.core.index import MaskIndex, MultiIndex
from climetlab.indexing.fieldset import FieldSet
from climetlab.utils.bbox import BoundingBox
from climetlab.utils.dates import to_datetime

from .coords import LevelCoordinate, OtherCoordinate, TimeCoordinate
from .dataset import DataSet
from .field import NetCDFField


class NetCDFFieldSet(FieldSet):
    def __init__(self, path):
        self.path = path
        self.opendap = path.startswith("http")

    @classmethod
    def new_mask_index(self, *args, **kwargs):
        return NetCDFMaskFieldSet(*args, **kwargs)

    def __repr__(self):
        return "NetCDFReader(%s)" % (self.path,)

    def __iter__(self):
        return iter(self.fields)

    def __len__(self):
        return len(self.fields)

    def __getitem__(self, n):
        return self.fields[n]

    @cached_property
    def dataset(self):
        import xarray as xr

        if ".zarr" in self.path:
            return xr.open_zarr(self.path)

        if self.opendap:
            return xr.open_dataset(self.path)
        else:
            return xr.open_mfdataset(self.path, combine="by_coords")

    @cached_property
    def fields(self):
        return self._get_fields(DataSet(self.dataset))

    def _get_fields(self, ds):  # noqa C901
        # Select only geographical variables
        has_lat = False
        has_lon = False

        fields = []

        skip = set()

        for name in ds.data_vars:
            v = ds[name]
            skip.update(getattr(v, "coordinates", "").split(" "))
            skip.update(getattr(v, "bounds", "").split(" "))
            skip.update(getattr(v, "grid_mapping", "").split(" "))

        for name in ds.data_vars:
            if name in skip:
                continue

            v = ds[name]

            coordinates = []

            # self.log.info('Scanning file: %s var=%s coords=%s', self.path, name, v.coords)

            info = [value for value in v.coords if value not in v.dims]
            non_dim_coords = {}
            for coord in v.coords:
                if coord not in v.dims:
                    non_dim_coords[coord] = ds[coord].values
                    continue

                c = ds[coord]

                # self.log.info("COORD %s %s %s %s", coord, type(coord), hasattr(c, 'calendar'), c)

                standard_name = getattr(c, "standard_name", None)
                axis = getattr(c, "axis", None)
                long_name = getattr(c, "long_name", None)

                use = False

                if (
                    standard_name in ("longitude", "projection_x_coordinate")
                    or (long_name == "longitude")
                    or (axis == "X")
                ):
                    has_lon = True
                    use = True

                if (
                    standard_name in ("latitude", "projection_y_coordinate")
                    or (long_name == "latitude")
                    or (axis == "Y")
                ):
                    has_lat = True
                    use = True

                # Of course, not every one sets the standard_name
                if standard_name in ("time", "forecast_reference_time") or axis == "T":
                    coordinates.append(TimeCoordinate(c, coord in info))
                    use = True

                # TODO: Support other level types
                if standard_name in (
                    "air_pressure",
                    "model_level_number",
                    "altitude",
                ):  # or axis == 'Z':
                    coordinates.append(LevelCoordinate(c, coord in info))
                    use = True

                if axis in ("X", "Y"):
                    use = True

                if not use:
                    coordinates.append(OtherCoordinate(c, coord in info))

            if not (has_lat and has_lon):
                # self.log.info("NetCDFReader: skip %s (Not a 2 field)", name)
                continue

            for values in product(*[c.values for c in coordinates]):
                slices = []
                for value, coordinate in zip(values, coordinates):
                    slices.append(coordinate.make_slice(value))

                fields.append(NetCDFField(self, ds, name, slices, non_dim_coords))

        if not fields:
            raise Exception("NetCDFReader no 2D fields found in %s" % (self.path,))

        return fields

    def to_xarray(self, **kwargs):
        import xarray as xr

        if self.path.startswith("http"):
            return xr.open_dataset(self.path, **kwargs)
        return type(self).to_xarray_multi_from_paths([self.path], **kwargs)

    @classmethod
    def to_xarray_multi_from_paths(cls, paths, **kwargs):
        import xarray as xr

        options = dict()
        options.update(kwargs.get("xarray_open_mfdataset_kwargs", {}))

        return xr.open_mfdataset(
            paths,
            **options,
        )

    def to_metview(self):
        from climetlab.metview import mv_read

        return mv_read(self.path)

    def plot_map(self, *args, **kwargs):
        return self.fields[0].plot_map(*args, **kwargs)

    # Used by normalisers
    def to_datetime(self):
        times = self.to_datetime_list()
        assert len(times) == 1
        return times[0]

    def to_datetime_list(self):
        # TODO: check if that can be done faster
        result = set()
        for s in self.fields:
            result.add(to_datetime(s.time))
        return sorted(result)

    def to_bounding_box(self):
        return BoundingBox.multi_merge([s.to_bounding_box() for s in self.fields])

    @classmethod
    def merge(cls, sources):
        assert len(sources) > 1
        assert all(isinstance(_, NetCDFFieldSet) for _ in sources)
        return NetCDFMultiFieldSet(sources)


class NetCDFMaskFieldSet(NetCDFFieldSet, MaskIndex):
    def __init__(self, *args, **kwargs):
        MaskIndex.__init__(self, *args, **kwargs)
        self.path = "<mask>"

    def __iter__(self):
        return MaskIndex.__iter__(self)

    def __len__(self):
        return MaskIndex.__len__(self)

    def __getitem__(self, n):
        return MaskIndex.__getitem__(self, n)


class NetCDFMultiFieldSet(NetCDFFieldSet, MultiIndex):
    def __init__(self, *args, **kwargs):
        MultiIndex.__init__(self, *args, **kwargs)
        self.paths = [s.path for s in args[0]]
        self.path = "<multi>"

    def to_xarray(self, **kwargs):
        import xarray as xr

        if not kwargs:
            kwargs = dict(combine="by_coords")
        return xr.open_mfdataset(self.paths, **kwargs)

    @cached_property
    def dataset(self):
        return self.to_xarray(combine="by_coords")

    def __iter__(self):
        return MaskIndex.__iter__(self)

    def __len__(self):
        return MaskIndex.__len__(self)

    def __getitem__(self, n):
        return MaskIndex.__getitem__(self, n)
