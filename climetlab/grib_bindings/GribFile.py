# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from .bindings import (
    grib_file_open,
    grib_handle_delete,
    grib_get,
    grib_values,
    GribError,
)


class GribField:
    def __init__(self, handle, path, offset):
        self._delete = grib_handle_delete
        self.handle = handle
        self.path = path
        self.offset = offset

    def __del__(self):
        self._delete(self.handle)

    def get(self, name):
        try:
            if name == "values":
                return grib_values(self.handle)
            return grib_get(self.handle, name)
        except GribError as e:
            if e.err == -10:  # Key not found
                return None
            raise


class GribFile:
    def __init__(self, path):
        self.path = path
        self.file = grib_file_open(path)

    def __del__(self):
        try:
            self.file.close()
        except Exception:
            pass

    def __iter__(self):
        return self

    def __next__(self):
        here = self.file.tell()
        h = self.file.next()
        if not h:
            raise StopIteration()
        return GribField(h, self.path, here)

    def at_offset(self, offset):
        self.file.position(offset)
        return self.__next__()
