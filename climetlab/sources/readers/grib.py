# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import logging

LOG = logging.getLogger(__name__)

try:
    from climetlab.grib_bindings import GribFile

    class Reader(GribFile):
        pass

    LOG.info("Using eccodes C bindings to decode GRIB data")

except AttributeError:  # eccodes not installed
    import pyeccodes

    class Reader(pyeccodes.Reader):
        def at_offset(self, offset):
            self.seek(offset)
            return next(self)

    LOG.info("Using pyeccodes to decode GRIB data")


class GribField:
    def __init__(self, handle, path):
        self.handle = handle
        self.path = path

    @property
    def values(self):
        return self.handle.get("values")

    def plot_map(self, driver):
        driver.bounding_box(
            north=self.handle.get("latitudeOfFirstGridPointInDegrees"),
            south=self.handle.get("latitudeOfLastGridPointInDegrees"),
            west=self.handle.get("longitudeOfFirstGridPointInDegrees"),
            east=self.handle.get("longitudeOfLastGridPointInDegrees"),
        )
        driver.plot_grib(self.path, self.handle.get("offset"))

    def to_numpy(self):
        return self.values.reshape((self.handle.get("Nj"), self.handle.get("Ni")))

    @property
    def offset(self):
        return int(self.handle.get("offset"))

    def __repr__(self):
        return "GribField(%s,%s,%s,%s,%s,%s)" % (
            self.handle.get("shortName"),
            self.handle.get("levelist"),
            self.handle.get("date"),
            self.handle.get("time"),
            self.handle.get("step"),
            self.handle.get("number"),
        )

    def grid_definition(self):
        return dict(
            north=self.handle.get("latitudeOfFirstGridPointInDegrees"),
            south=self.handle.get("latitudeOfLastGridPointInDegrees"),
            west=self.handle.get("longitudeOfFirstGridPointInDegrees"),
            east=self.handle.get("longitudeOfLastGridPointInDegrees"),
            south_north_increment=self.handle.get("jDirectionIncrementInDegrees"),
            west_east_increment=self.handle.get("iDirectionIncrementInDegrees"),
        )

    def metadata(self):
        m = dict()
        for n in ("shortName", "units"):
            p = self.handle.get(n)
            if p is not None:
                m[n] = str(p)

        return m


class GRIBIterator:
    def __init__(self, path):
        self.path = path
        self.reader = Reader(path)

    def __repr__(self):
        return "GRIBIterator(%s)" % (self.path,)

    def __next__(self):
        return GribField(next(self.reader), self.path)


class GRIBReader:
    def __init__(self, path):
        self.path = path
        self._fields = None
        self._reader = None

    def __repr__(self):
        return "GRIBReader(%s)" % (self.path,)

    def __iter__(self):
        return GRIBIterator(self.path)

    def _items(self):
        if self._fields is None:
            self._fields = []
            # print("Scan", self.path)
            for f in self:
                self._fields.append(f.offset)
        return self._fields

    def __getitem__(self, n):
        if self._reader is None:
            self._reader = Reader(self.path)
        return GribField(self._reader.at_offset(self._items()[n]), self.path)

    def __len__(self):
        return len(self._items())

    def to_xarray(self):
        import xarray as xr

        return xr.open_dataset(self.path, engine="cfgrib")
