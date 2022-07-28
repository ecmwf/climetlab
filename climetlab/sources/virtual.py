# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import calendar
import datetime
import logging

import climetlab as cml
from climetlab.readers.grib.index import GribIndex

LOG = logging.getLogger(__name__)


class VirtualField:
    def __init__(self, reference, h):
        date = datetime.datetime(1959, 1, 1) + datetime.timedelta(hours=h)
        self.date = date.year * 10000 + date.month * 100 + date.day
        self.time = date.hour
        self.reference = reference
        self.Nx = reference["Nx"]
        self.Ny = reference["Ny"]

    def metadata(self, n):
        if n == "dataDate":
            return self.date

        if n == "dataTime":
            return self.time

        return self.reference[n]

    @property
    def values(self):
        yyyymm, dd = self.date // 100, self.date % 100

        yyyy = yyyymm // 100
        mm = yyyymm % 100
        last = calendar.monthrange(yyyy, mm)[1]
        fields = cml.load_source(
            "cds",
            "reanalysis-era5-single-levels",
            product_type="reanalysis",
            year=yyyy,
            month=mm,
            day=list(range(1, last + 1)),
            param="2t",
            time=list(range(0, 24)),
            grid="10/10",
        )

        return fields[(dd - 1) * 24 + self.time].values


class NoLock:
    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass


class Virtual(GribIndex):
    SIZE = int(365.25 * 24 * (2022 - 1959))

    def __init__(self):
        super().__init__()
        self.reference = cml.load_source(
            "cds",
            "reanalysis-era5-single-levels",
            product_type="reanalysis",
            date=19590101,
            param="2t",
            time=0,
            grid="10/10",
        )[0]

    def __len__(self):
        return self.SIZE

    def __getitem__(self, i):
        if i >= self.SIZE:
            raise IndexError()

        return VirtualField(self.reference, i)

    def xarray_open_dataset_kwargs(self):
        return dict(
            cache=False,  # Set to false to prevent loading the whole dataset
            chunks={
                "time": 24 * 31,
                # "step": 1,
                # "number": 1,
                # "surface": 1,
                "latitude": 721,
                "longitude": 1440,
            },
            lock=NoLock(),
        )


source = Virtual
