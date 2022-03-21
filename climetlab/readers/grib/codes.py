# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import json
import logging
import os

import eccodes

from climetlab.core import Base
from climetlab.core.caching import auxiliary_cache_file
from climetlab.profiling import call_counter
from climetlab.utils.bbox import BoundingBox

LOG = logging.getLogger(__name__)


def missing_is_none(x):
    return None if x == 2147483647 else x


# This does not belong here, should be in the C library
def _get_message_offsets(path):

    fd = os.open(path, os.O_RDONLY)
    try:

        def get(count):
            buf = os.read(fd, count)
            assert len(buf) == count
            return int.from_bytes(
                buf,
                byteorder="big",
                signed=False,
            )

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
                    flags = get(1)
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
            size = eccodes.codes_get_size(self.handle, name)
            LOG.debug(f"{name}:{size}")
            if size and size > 1:
                return eccodes.codes_get_array(self.handle, name)
            return eccodes.codes_get(self.handle, name)
        except eccodes.KeyValueNotFoundError:
            return None

    def get_long(self, name):
        try:
            return eccodes.codes_get_long(self.handle, name)
        except eccodes.KeyValueNotFoundError:
            return None

    def get_string(self, name):
        try:
            return eccodes.codes_get_string(self.handle, name)
        except eccodes.KeyValueNotFoundError:
            return None

    def get_double(self, name):
        try:
            return eccodes.codes_get_double(self.handle, name)
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

    def read(self, offset, length):
        self.file.seek(offset, 0)
        return self.file.read(length)


class GribField(Base):
    def __init__(self, reader, offset, length):
        self._reader = reader
        self._offset = offset
        self._length = length
        self._handle = None

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
        return (
            missing_is_none(self.handle.get("Nj")),
            missing_is_none(self.handle.get("Ni")),
        )

    def plot_map(self, backend):
        backend.bounding_box(
            north=self.handle.get("latitudeOfFirstGridPointInDegrees"),
            south=self.handle.get("latitudeOfLastGridPointInDegrees"),
            west=self.handle.get("longitudeOfFirstGridPointInDegrees"),
            east=self.handle.get("longitudeOfLastGridPointInDegrees"),
        )
        backend.plot_grib(self.path, self.handle.get("offset"))

    @call_counter
    def to_numpy(self, normalise=False):
        shape = self.shape
        if shape[0] is None or shape[1] is None:
            return self.values
        if normalise:
            return self.values.reshape(self.shape)
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
            date // 10000,
            date % 10000 // 100,
            date % 100,
            time // 100,
            time % 100,
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

    def _get(self, name):
        """Private, for testing only"""
        # paramId is renamed as param to get rid of the
        # additional '.128' (in climetlab/scripts/grib.py)
        if name == "param":
            name = "paramId"
        return self.handle.get(name)

    def __getitem__(self, name):
        """For cfgrib"""

        # print(name)

        proc = self.handle.get
        if ":" in name:
            try:
                name, kind = name.split(":")
                proc = dict(
                    str=self.handle.get_string,
                    int=self.handle.get_long,
                    float=self.handle.get_double,
                )[kind]
            except Exception:
                LOG.exception(f"Unsupported kind '{kind}'")
                raise ValueError(f"Unsupported kind '{kind}'")

        return proc(name)

    def write(self, f):
        f.write(self._reader.read(self._offset, self._length))


class GribIndex:

    VERSION = 1

    def __init__(self, path):
        assert isinstance(path, str), path
        self.path = path
        self.offsets = None
        self.lengths = None
        self.cache = auxiliary_cache_file(
            "grib-index",
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
