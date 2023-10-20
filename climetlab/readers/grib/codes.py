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
import os
import threading
import time
from itertools import islice

import eccodes

from climetlab.core import Base
from climetlab.core.constants import DATETIME
from climetlab.profiling import call_counter
from climetlab.utils.bbox import BoundingBox

LOG = logging.getLogger(__name__)


def missing_is_none(x):
    return None if x == 2147483647 else x


# This does not belong here, should be in the C library
def get_messages_positions(path):
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

# For some reason, cffi can ge stuck in the GC if that function
# needs to be called defined for the first time in a GC thread.
try:
    _h = eccodes.codes_new_from_samples(
        "regular_ll_pl_grib1", eccodes.CODES_PRODUCT_GRIB
    )
    eccodes.codes_release(_h)
except:  # noqa E722
    pass


class CodesHandle:
    def __init__(self, handle, path, offset):
        self.handle = handle
        self.path = path
        self.offset = offset

    @classmethod
    def from_sample(cls, name):
        return cls(
            eccodes.codes_new_from_samples(name, eccodes.CODES_PRODUCT_GRIB), None, None
        )

    def __del__(self):
        try:
            eccodes_codes_release(self.handle)
        except TypeError:
            # This happens when eccodes is unloaded before
            # this object is deleted
            pass

    def get(self, name):
        try:
            if name == "values":
                return eccodes.codes_get_values(self.handle)
            size = eccodes.codes_get_size(self.handle, name)
            # LOG.debug(f"{name}:{size}")

            if name == "md5GridSection":
                # Special case because:
                #
                # 1) eccodes is returning size > 1 for 'md5GridSection'
                # (size = 16 : it is the number of bytes of the value)
                # This will be fixed in eccodes.
                #
                # 2) sometimes (see below), the value for "shapeOfTheEarth" is inconsistent.
                # This impacts the (computed on-the-fly) value of "md5GridSection".
                # ----------------
                # Example of data with inconsistent values:
                # S2S data, origin='ecmf', param='tp', step='24', number='0', date=['20201203','20200702']
                # the 'md5GridSection' are different
                # This is because one has "shapeOfTheEarth" set to 0, the other to 6.
                # This is only impacting the metadata.
                # Since this has no impact on the data itself,
                # this is unlikely to be fixed. Therefore this hacky patch.
                #
                # Obviously, the patch causes an inconsistency between the value of md5GridSection
                # read by this code, and the value read by another code without this patch.

                save = eccodes.codes_get_long(self.handle, "shapeOfTheEarth")
                eccodes.codes_set_long(self.handle, "shapeOfTheEarth", 255)
                result = eccodes.codes_get_string(self.handle, "md5GridSection")
                eccodes.codes_set_long(self.handle, "shapeOfTheEarth", save)
                return result

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

    def get_data(self):
        return eccodes.codes_grib_get_data(self.handle)

    def as_mars(self, param="shortName"):
        r = {}
        it = eccodes.codes_keys_iterator_new(self.handle, "mars")

        try:
            while eccodes.codes_keys_iterator_next(it):
                key = eccodes.codes_keys_iterator_get_name(it)
                r[key] = self.get(param if key == "param" else key)
        finally:
            eccodes.codes_keys_iterator_delete(it)

        return r

    def clone(self):
        return CodesHandle(eccodes.codes_clone(self.handle), None, None)

    def set_values(self, values):
        assert self.path is None, "Only cloned handles can have values changed"
        eccodes.codes_set_values(self.handle, values.flatten())
        # This is writing on the GRIB that something has been modified (255=unknown)
        eccodes.codes_set_long(self.handle, "generatingProcessIdentifier", 255)

    def set_multiple(self, values):
        assert self.path is None, "Only cloned handles can have values changed"
        eccodes.codes_set_key_vals(self.handle, values)

    def set_long(self, name, value):
        try:
            assert self.path is None, "Only cloned handles can have values changed"
            eccodes.codes_set_long(self.handle, name, value)
        except Exception as e:
            LOG.error("Error setting %s=%s", name, value)
            raise ValueError("Error setting %s=%s (%s)" % (name, value, e))

    def set_double(self, name, value):
        try:
            assert self.path is None, "Only cloned handles can have values changed"
            eccodes.codes_set_double(self.handle, name, value)
        except Exception as e:
            LOG.error("Error setting %s=%s", name, value)
            raise ValueError("Error setting %s=%s (%s)" % (name, value, e))

    def set_string(self, name, value):
        try:
            assert self.path is None, "Only cloned handles can have values changed"
            eccodes.codes_set_string(self.handle, name, value)
        except Exception as e:
            LOG.error("Error setting %s=%s", name, value)
            raise ValueError("Error setting %s=%s (%s)" % (name, value, e))

    def set(self, name, value):
        try:
            assert self.path is None, "Only cloned handles can have values changed"

            if isinstance(value, list):
                return eccodes.codes_set_array(self.handle, name, value)

            return eccodes.codes_set(self.handle, name, value)
        except Exception as e:
            LOG.error("Error setting %s=%s", name, value)
            raise ValueError("Error setting %s=%s (%s)" % (name, value, e))

    def write(self, f):
        eccodes.codes_write(self.handle, f)

    def save(self, path):
        with open(path, "wb") as f:
            eccodes.codes_write(self.handle, f)
            self.path = path
            self.offset = 0

    def read_bytes(self, offset, length):
        with open(self.path, "rb") as f:
            f.seek(offset)
            return f.read(length)


class ReaderLRUCache(dict):
    def __init__(self, size):
        self.readers = dict()
        self.lock = threading.Lock()
        self.size = size

    def __getitem__(self, path):
        key = (
            path,
            os.getpid(),
        )  # PyTorch will fork and leave the cache in a funny state
        with self.lock:
            try:
                return super().__getitem__(key)
            except KeyError:
                pass

            c = self[key] = CodesReader(path)

            while len(self) >= self.size:
                _, oldest = min((v.last, k) for k, v in self.items())
                del self[oldest]

            return c


cache = ReaderLRUCache(512)  # TODO: Add to config


class CodesReader:
    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()
        self.file = open(self.path, "rb")
        self.last = time.time()

    def __del__(self):
        try:
            self.file.close()
        except Exception:
            pass

    @classmethod
    def from_cache(cls, path):
        return cache[path]

    def at_offset(self, offset):
        with self.lock:
            self.last = time.time()
            self.file.seek(offset, 0)
            handle = eccodes_codes_new_from_file(
                self.file,
                eccodes.CODES_PRODUCT_GRIB,
            )
            assert handle is not None, (self.file, offset)
            return CodesHandle(handle, self.path, offset)


class GribField(Base):
    def __init__(self, path, offset, length):
        self.path = path
        self._offset = offset
        self._length = length
        self._handle = None
        self._values = None
        self._cache = {}

    @property
    def handle(self):
        if self._handle is None:
            assert self._offset is not None
            self._handle = CodesReader.from_cache(self.path).at_offset(self._offset)
        return self._handle

    @property
    def values(self):
        if self._values is None:
            self._values = self.handle.get("values")
        return self._values

    @property
    def offset(self):
        if self._offset is None:
            self._offset = int(self.handle.get("offset"))
        return self._offset

    @property
    def shape(self):
        Nj = missing_is_none(self.handle.get("Nj"))
        Ni = missing_is_none(self.handle.get("Ni"))
        if Ni is None or Nj is None:
            n = self.handle.get("numberOfDataPoints")
            return (n,)  # shape must be a tuple
        return (Nj, Ni)

    def plot_map(self, backend):
        backend.bounding_box(
            north=self.handle.get("latitudeOfFirstGridPointInDegrees"),
            south=self.handle.get("latitudeOfLastGridPointInDegrees"),
            west=self.handle.get("longitudeOfFirstGridPointInDegrees"),
            east=self.handle.get("longitudeOfLastGridPointInDegrees"),
        )
        backend.plot_grib(self.path, self.handle.get("offset"))

    @call_counter
    def to_numpy(self, reshape=True, dtype=None):
        values = self.values
        if reshape:
            values = values.reshape(self.shape)
        if dtype is not None:
            values = values.astype(dtype)
        return values

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

        for n in (
            "shortName",
            "units",
            "paramId",
            "level",
            "typeOfLevel",
            "marsClass",
            "marsStream",
            "marsType",
            "number",
            "stepRange",
            "param",
            "long_name",
            "standard_name",
            "levelist",
        ):
            p = self.handle.get(n)
            if p is not None:
                m[n] = str(p)
        m["shape"] = self.shape
        return m

    @property
    def resolution(self):
        grid_type = self["gridType"]

        if grid_type == "reduced_gg":
            return self["gridName"]

        if grid_type == "regular_ll":
            x = self["DxInDegrees"]
            y = self["DyInDegrees"]
            assert x == y, (x, y)
            return x

        raise ValueError(f"Unknown gridType={grid_type}")

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
        date = self.handle.get("validityDate")
        time = self.handle.get("validityTime")
        return datetime.datetime(
            date // 10000,
            date % 10000 // 100,
            date % 100,
            time // 100,
            time % 100,
        )

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

    def metadata(self, name):
        if name == DATETIME:
            date = self.metadata("validityDate")
            time = self.metadata("validityTime")
            return datetime.datetime(
                date // 10000,
                date % 10000 // 100,
                date % 100,
                time // 100,
                time % 100,
            ).isoformat()

        if name == "param":
            name = "shortName"

        if name == "_param_id":
            name = "paramId"

        if name == "level" and self[name] == 0:
            return None

        return self[name]

    def __getitem__(self, name):
        """For cfgrib"""

        if name not in self._cache:
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

            self._cache[name] = proc(name)

        return self._cache[name]

    @property
    def data(self):
        return self.handle.get_data()

    def as_mars(self, param="shortName"):
        return self.handle.as_mars(param)

    def write(self, f):
        f.write(self.handle.read_bytes(self._offset, self._length))

    def plot_numpy(self, backend, array):
        if self.handle.get("gridType") == "regular_ll":
            metadata = self.field_metadata()

            backend.bounding_box(
                north=metadata["north"],
                south=metadata["south"],
                west=metadata["west"],
                east=metadata["east"],
            )

            backend.plot_numpy(
                array.reshape(metadata.get("shape", self.shape)),
                metadata=metadata,
            )
            return

        # Non-regular field
        tmp = backend.temporary_file(".grib")
        clone = self.handle.clone()
        clone.set_values(array)
        clone.save(tmp)
        GribField(tmp, 0, self._length).plot_map(backend)

    def iterate_grid_points(self):
        latlon = self.handle.get("latitudeLongitudeValues")
        yield from zip(islice(latlon, 0, None, 3), islice(latlon, 1, None, 3))

    def grid_points(self):
        import numpy as np

        data = self.data
        lat = np.array([d["lat"] for d in data])
        lon = np.array([d["lon"] for d in data])

        return lat, lon
