# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import copy

# import atexit
import datetime
import json
import logging
import os

import eccodes

from climetlab.core import Base
from climetlab.core.caching import auxiliary_cache_file
from climetlab.profiling import call_counter

# from climetlab.decorators import dict_args
from climetlab.utils.bbox import BoundingBox

from . import Reader

# from collections import defaultdict


LOG = logging.getLogger(__name__)


def mix_kwargs(user, default, forced={}, logging_owner="", logging_main_key=""):
    kwargs = copy.deepcopy(default)

    for k, v in user.items():
        if k in forced and v != forced[k]:
            LOG.warning(
                (
                    f"In {logging_owner} {logging_main_key},"
                    f"ignoring attempt to override {k}={forced[k]} with {k}={v}."
                )
            )
            continue

        if k in default and v != default[k]:
            LOG.warning(
                (
                    f"In {logging_owner} {logging_main_key}, overriding the default value "
                    f"({k}={default[k]}) with {k}={v} is not recommended."
                )
            )

        kwargs[k] = v

    kwargs.update(forced)

    return kwargs


# This does not belong here, should be in the C library
def _get_message_offsets(path):

    fd = os.open(path, os.O_RDONLY)
    try:

        def get(count):
            buf = os.read(fd, count)
            assert len(buf) == count
            n = 0
            for i in buf:
                n = n * 256 + int(i)
            return n

        offset = 0
        while True:
            code = os.read(fd, 4)
            if len(code) < 4:
                break

            if code != b"GRIB":
                offset = os.lseek(fd, offset + 1, os.SEEK_SET)
                continue

            length = get(3)
            edition = get(1)

            if edition == 1:
                if length & 0x800000:
                    sec1len = get(3)
                    os.lseek(fd, 4, os.SEEK_CUR)
                    flags = int(os.read(fd, 1))
                    os.lseek(fd, sec1len - 8, os.SEEK_CUR)

                    if flags & (1 << 7):
                        sec2len = get(3)
                        os.lseek(fd, sec2len - 3, os.SEEK_CUR)

                    if flags & (1 << 6):
                        sec3len = get(3)
                        os.lseek(fd, sec3len - 3, os.SEEK_CUR)

                    sec4len = get(3)

                    if sec4len < 120:
                        length &= 0x7FFFFF
                        length *= 120
                        length -= sec4len
                        length += 4

            if edition == 2:
                length = get(8)

            yield offset, length
            offset = os.lseek(fd, offset + length, os.SEEK_SET)

    finally:
        os.close(fd)


eccodes_codes_release = call_counter(eccodes.codes_release)
eccodes_codes_new_from_file = call_counter(eccodes.codes_new_from_file)


class CodesHandle:
    def __init__(self, handle, path, offset):
        self.handle = handle
        self.path = path
        self.offset = offset

    def __del__(self):
        eccodes_codes_release(self.handle)

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
        return next(self)

    def __iter__(self):
        return self

    def __next__(self):
        handle = self._next_handle()
        if handle is None:
            raise StopIteration()
        return handle

    def _next_handle(self):
        offset = self.file.tell()
        handle = eccodes_codes_new_from_file(self.file, eccodes.CODES_PRODUCT_GRIB)
        if not handle:
            return None
        return CodesHandle(handle, self.path, offset)

    @property
    def offset(self):
        return self.file.tell()


class GribField(Base):
    def __init__(self, *, handle=None, reader=None, offset=None):
        assert reader
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

    @call_counter
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


# class MultiGribReaders(GriddedMultiReaders):
#     engine = "cfgrib"
#     backend_kwargs = {"squeeze": False}


class GRIBIndex:

    VERSION = 1

    def __init__(self, path):
        self.path = path
        self.offsets = None
        self.lengths = None
        self.cache = auxiliary_cache_file(
            "grib",
            path,
            content="null",
            extension=".json",
        )

        if not self._load_cache():
            self._build_index()

    def _build_index(self):

        offsets = []
        lengths = []

        for offset, length in _get_message_offsets(self.path):
            offsets.append(offset)
            lengths.append(length)

        self.offsets = offsets
        self.lengths = lengths

        self._save_cache()

    def _save_cache(self):
        try:
            with open(self.cache, "w") as f:
                json.dump(
                    dict(
                        version=self.VERSION,
                        offsets=self.offsets,
                        lengths=self.lengths,
                    ),
                    f,
                )
        except Exception:
            LOG.exception("Write to cache failed %s", self.cache)

    def _load_cache(self):
        try:
            with open(self.cache) as f:
                c = json.load(f)
                if not isinstance(c, dict):
                    return False

                assert c["version"] == self.VERSION
                self.offsets = c["offsets"]
                self.lengths = c["lengths"]
                return True
        except Exception:
            LOG.exception("Load from cache failed %s", self.cache)

        return False


class GRIBReader(Reader):
    appendable = True  # GRIB messages can be added to the same file

    open_mfdataset_backend_kwargs = {"squeeze": False}
    open_mfdataset_engine = "cfgrib"

    def __init__(self, source, path):
        super().__init__(source, path)
        self._index = None
        self._reader = None

    def __repr__(self):
        return "GRIBReader(%s)" % (self.path,)

    def __iter__(self):
        return GRIBIterator(self.path)

    @property
    def reader(self):
        if self._reader is None:
            self._reader = CodesReader(self.path)
        return self._reader

    @property
    def index(self):
        if self._index is None:
            self._index = GRIBIndex(self.path)
        return self._index

    def __getitem__(self, n):
        return GribField(
            reader=self.reader,
            offset=self.index.offsets[n],
        )

    @property
    def first(self):
        return GribField(reader=self.reader, offset=0)

    def __len__(self):
        return len(self.index.offsets)

    def to_xarray(self, **kwargs):
        return type(self).to_xarray_multi([self.path], **kwargs)

    def to_tfdataset(self, **kwargs):
        # assert "label" in kwargs
        if "label" in kwargs:
            return self._to_tfdataset_supervised(**kwargs)
        else:
            return self._to_tfdataset_unsupervised(**kwargs)

    def _to_tfdataset_unsupervised(self, **kwargs):
        def generate():
            for s in self:
                yield s.to_numpy()

        import tensorflow as tf

        # TODO check the cost of the conversion
        # maybe default to float64
        dtype = kwargs.get("dtype", tf.float32)
        return tf.data.Dataset.from_generator(generate, dtype)

    def _to_tfdataset_supervised(self, label, **kwargs):
        @call_counter
        def generate():
            for s in self:
                yield s.to_numpy(), s.handle.get(label)

        import tensorflow as tf

        # with timer("_to_tfdataset_supervised shape"):
        shape = self.first.shape

        # TODO check the cost of the conversion
        # maybe default to float64
        dtype = kwargs.get("dtype", tf.float32)
        # with timer("tf.data.Dataset.from_generator"):
        return tf.data.Dataset.from_generator(
            generate,
            output_signature=(
                tf.TensorSpec(shape, dtype=dtype, name="data"),
                tf.TensorSpec(tuple(), dtype=tf.int64, name=label),
            ),
        )

    @classmethod
    def to_xarray_multi(cls, paths, **kwargs):
        import xarray as xr

        xarray_open_mfdataset_kwargs = {}

        user_xarray_open_mfdataset_kwargs = kwargs.get(
            "xarray_open_mfdataset_kwargs", {}
        )
        for key in ["backend_kwargs"]:
            xarray_open_mfdataset_kwargs[key] = mix_kwargs(
                user=user_xarray_open_mfdataset_kwargs.pop(key, {}),
                default={"squeeze": False},
                forced={},
                logging_owner="xarray_open_mfdataset_kwargs",
                logging_main_key=key,
            )
        xarray_open_mfdataset_kwargs.update(
            mix_kwargs(
                user=user_xarray_open_mfdataset_kwargs,
                default={},
                forced={"engine": "cfgrib"},
            )
        )

        return xr.open_mfdataset(
            paths,
            **xarray_open_mfdataset_kwargs,
        )


def reader(source, path, magic, deeper_check):
    if magic[:4] == b"GRIB":
        return GRIBReader(source, path)
