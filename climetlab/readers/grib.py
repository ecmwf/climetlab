# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import logging

import eccodes

from climetlab.decorators import dict_args
from climetlab.utils.bbox import BoundingBox

from . import Reader

LOG = logging.getLogger(__name__)

# return eccodes.codes_new_from_file(self.file, eccodes.CODES_PRODUCT_GRIB)

# See https://pymotw.com/2/weakref/


class CodesHandle:
    def __init__(self, handle, path, offset):
        self.handle = handle
        self.path = path
        self.offset = offset

    def __del__(self):
        eccodes.codes_release(self.handle)

    def get(self, name):
        try:
            if name == "values":
                return eccodes.codes_get_values(self.handle)
            if name in ("distinctLatitudes", "distinctLongitudes"):
                return eccodes.codes_get_double_array(self.handle, name)
            return eccodes.codes_get(self.handle, name)
        except eccodes.KeyValueNotFoundError:
            return None


class CodesReader:
    def __init__(self, path):
        self.path = path
        self.file = open(self.path, "rb")

    def __del__(self):
        try:
            self.file.close()
        except Exception:
            pass

    def at_offset(self, offset):
        self.file.seek(offset, 0)
        return self.__next__()

    def __iter__(self):
        return self

    def __next__(self):
        offset = self.file.tell()
        handle = eccodes.codes_new_from_file(self.file, eccodes.CODES_PRODUCT_GRIB)
        if not handle:
            raise StopIteration()
        return CodesHandle(handle, self.path, offset)

    @property
    def offset(self):
        return self.file.tell()


def cb(r):
    print("Delete", r)


class GribField:
    def __init__(self, *, handle=None, reader=None, offset=None):
        self._handle = handle
        self._reader = reader
        self._offset = offset

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def path(self):
        return self.handle.path

    @property
    def handle(self):
        if self._handle is None:
            assert self._offset is not None
            assert self._reader is not None
            self._handle = self._reader.at_offset(self._offset)
        return self._handle

    @property
    def values(self):
        return self.handle.get("values")

    @property
    def offset(self):
        if self._offset is None:
            self._offset = int(self.handle.get("offset"))
        return self._offset

    @property
    def shape(self):
        return self.handle.get("Nj"), self.handle.get("Ni")

    def plot_map(self, driver):
        driver.bounding_box(
            north=self.handle.get("latitudeOfFirstGridPointInDegrees"),
            south=self.handle.get("latitudeOfLastGridPointInDegrees"),
            west=self.handle.get("longitudeOfFirstGridPointInDegrees"),
            east=self.handle.get("longitudeOfLastGridPointInDegrees"),
        )
        driver.plot_grib(self.path, self.handle.get("offset"))

    def to_numpy(self):
        return self.values.reshape(self.shape)

    def __repr__(self):
        return "GribField(%s,%s,%s,%s,%s,%s)" % (
            self.handle.get("shortName"),
            self.handle.get("levelist"),
            self.handle.get("date"),
            self.handle.get("time"),
            self.handle.get("step"),
            self.handle.get("number"),
        )

    def _grid_definition(self):
        return dict(
            north=self.handle.get("latitudeOfFirstGridPointInDegrees"),
            south=self.handle.get("latitudeOfLastGridPointInDegrees"),
            west=self.handle.get("longitudeOfFirstGridPointInDegrees"),
            east=self.handle.get("longitudeOfLastGridPointInDegrees"),
            south_north_increment=self.handle.get("jDirectionIncrementInDegrees"),
            west_east_increment=self.handle.get("iDirectionIncrementInDegrees"),
        )

    def field_metadata(self):
        m = self._grid_definition()
        for n in ("shortName", "units", "paramId"):
            p = self.handle.get(n)
            if p is not None:
                m[n] = str(p)
        m["shape"] = self.shape
        return m

    def helper(self):
        return self

    def datetime(self):
        date = self.handle.get("date")
        time = self.handle.get("time")
        return datetime.datetime(
            date // 10000, date % 10000 // 100, date % 100, time // 100, time % 100
        )

    def valid_datetime(self):
        step = self.handle.get("endStep")
        return self.datetime() + datetime.timedelta(hours=step)

    def to_datetime_list(self):
        return [self.valid_datetime()]

    def to_bounding_box(self):
        return BoundingBox(
            north=self.handle.get("latitudeOfFirstGridPointInDegrees"),
            south=self.handle.get("latitudeOfLastGridPointInDegrees"),
            west=self.handle.get("longitudeOfFirstGridPointInDegrees"),
            east=self.handle.get("longitudeOfLastGridPointInDegrees"),
        )

    def _attributes(self, names):
        result = {}
        for name in names:
            result[name] = self.handle.get(name)
        return result


class GRIBIterator:
    def __init__(self, path):
        self.path = path
        self.reader = CodesReader(path)

    def __repr__(self):
        return "GRIBIterator(%s)" % (self.path,)

    def __next__(self):
        offset = self.reader.offset
        handle = next(self.reader)
        return GribField(handle=handle, reader=self.reader, offset=offset)

    def __iter__(self):
        return self


class GRIBFilter:
    def __init__(self, reader, filter):
        self._reader = reader
        self._filter = dict(**filter)

    def __repr__(self):
        return "GRIBFilter(%s, %s)" % (self._reader, self._filter)

    def __iter__(self):
        return GRIBIterator(self.path)


class GRIBMultiFileReader(Reader):
    def __init__(self, source, readers):
        super().__init__(source, "/-multi-")


class OLDGRIBReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)
        self._fields = None
        self._reader = None

    def __repr__(self):
        return "GRIBReader(%s)" % (self.path,)

    def __iter__(self):
        return GRIBIterator(self.path)

    def _items(self):
        if self._fields is None:
            self._fields = []
            for f in self:
                self._fields.append(f.offset)
        return self._fields

    def __getitem__(self, n):
        if self._reader is None:
            self._reader = CodesReader(self.path)
        return GribField(reader=self._reader, offset=self._items()[n])

    def __len__(self):
        return len(self._items())

    def to_xarray(self):
        import xarray as xr

        params = self.source.cfgrib_options()
        ds = xr.open_dataset(self.path, engine="cfgrib", **params)
        return self.source.post_xarray_open_dataset_hook(ds)

    @dict_args
    def sel(self, **kwargs):
        return GRIBFilter(self, kwargs)

    def multi_merge(source, readers):
        return GRIBMultiFileReader(source, readers)


class GRIBReader(Reader):
    def __init__(self, source, paths=None, fields=[], filter=None, unfiltetered=True):
        super().__init__(source, paths)
        self._fields = [f for f in fields]
        self._unfiltetered = unfiltetered

        if paths is not None:
            if not isinstance(paths, (list, tuple)):
                paths = [paths]
            for path in paths:
                for f in GRIBIterator(path):
                    self._fields.append(f)

    def __getitem__(self, n):
        return self._fields[n]

    def __len__(self):
        return len(self._fields)

    def _attributes(self, names):
        result = []
        for field in self:
            result.append(field._attributes(names))
        return result

    def multi_merge(source, readers):
        fields = []
        paths = []
        for r in readers:
            fields += r._fields
            if isinstance(r.path, (list, tuple)):
                paths += list(r.path)
            else:
                paths.append(r.path)

        return GRIBReader(
            source,
            paths=paths,
            # fields=fields,
            unfiltetered=all(r._unfiltetered for r in readers),
        )

    def to_xarray(self):
        assert self._unfiltetered
        assert self.path

        import xarray as xr

        params = self.source.cfgrib_options()
        if isinstance(self.path, (list, tuple)):
            ds = xr.open_mfdataset(self.path, engine="cfgrib", **params)
        else:
            ds = xr.open_dataset(self.path, engine="cfgrib", **params)
        return self.source.post_xarray_open_dataset_hook(ds)


class Field:
    def __init__(self, field):
        self.field = field

    def __getitem__(self, key):
        print("field", key)
        v = self.field.handle.get(key)
        return v


class FieldSetIndex:
    def __init__(
        self,
        source,
        *,
        filter_by_keys={},
        grib_errors="warn",
        index_keys=[],
        read_keys=[],
        items=None,
    ):
        self.source = source
        self.filter_by_keys = filter_by_keys
        self.grib_errors = grib_errors
        self.index_keys = index_keys
        self.read_keys = read_keys
        self.items = items

    def __call__(self, *, grib_errors, index_keys, read_keys, **kwargs):
        return FieldSetIndex(
            source=self.source,
            filter_by_keys=self.filter_by_keys,
            grib_errors=grib_errors,
            index_keys=index_keys,
            read_keys=read_keys,
            items=self.items,
        )

    def subindex(self, filter_by_keys={}, **kwargs):
        query = dict(**self.filter_by_keys)
        query.update(filter_by_keys)
        query.update(kwargs)
        return FieldSetIndex(
            source=self.source,
            filter_by_keys=query,
            grib_errors=self.grib_errors,
            index_keys=self.index_keys,
            read_keys=self.read_keys,
            items=self.items,
        )

    def _valid(self, item):
        for k, v in self.filter_by_keys.items():
            if item.get(k) != v:
                return False
        return True

    def _valid_items(self):
        if self.items is None:
            self.items = self.source._attributes(self.index_keys)

        return [i for i in self.items if self._valid(i)]

    def __getitem__(self, key):

        x = [i[key] for i in self._valid_items()]
        if None in x:
            return []

        print("GET", key, x)
        return list(set(x))

    def getone(self, key):
        return self[key][0]

    @property
    def offsets(self):
        for i, item in enumerate(self._valid_items()):
            yield item, i

    @property
    def filestream(self):
        return self

    @property
    def path(self):
        return None

    def first(self):
        return Field(self.source[0])
