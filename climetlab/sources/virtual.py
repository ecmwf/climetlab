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
import threading

import climetlab as cml
from climetlab.readers.grib.index import GribIndex

LOG = logging.getLogger(__name__)


class NoLock:
    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass


class VirtualField:
    def __init__(self, h, owner):
        self.owner = owner
        date = datetime.datetime(1959, 1, 1) + datetime.timedelta(hours=h)
        self.date = date.year * 10000 + date.month * 100 + date.day
        self.time = date.hour

    def metadata(self, n):
        if n == "dataDate":
            return self.date

        if n == "dataTime":
            return self.time

        return self.owner.reference[n]

    @property
    def values(self):
        fields = self.owner.field(self.date)
        dd = self.date % 100
        return fields[(dd - 1) * 24 + self.time].values


class DictOveray(dict):
    def __init__(self, field):
        self.field = field

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            self[key] = self.field[key]
            return self[key]


class Virtual(GribIndex):
    SIZE = int(365.25 * 24 * (2022 - 1959))
    # SIZE = 100

    DATASET = dict(
        dataset="reanalysis-era5-single-levels",
        product_type="reanalysis",
        param="msl",
        grid="10/10",
    )

    def __init__(self):
        super().__init__()
        self.reference = DictOveray(
            cml.load_source(
                "cds",
                date=19590101,
                time=0,
                **self.DATASET,
            )[0]
        )

        self.fields = {}
        self.lock = threading.Lock()
        self.locks = {}

    def __len__(self):
        return self.SIZE

    def __getitem__(self, i):
        if i >= self.SIZE:
            raise IndexError()

        return VirtualField(i, self)

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

    def field(self, date):

        yyyymm = date // 100

        with self.lock:
            if yyyymm in self.fields:
                return self.fields[yyyymm]
            if yyyymm not in self.locks:
                self.locks[yyyymm] = threading.Lock()

        with self.locks[yyyymm]:

            # Some other threads may have created that in the meantime

            if yyyymm in self.fields:
                return self.fields[yyyymm]

            yyyy = yyyymm // 100
            mm = yyyymm % 100
            last = calendar.monthrange(yyyy, mm)[1]
            fields = cml.load_source(
                "cds",
                year=yyyy,
                month=mm,
                day=list(range(1, last + 1)),
                time=list(range(0, 24)),
                **self.DATASET,
            )
            self.fields[yyyymm] = fields
            return fields


source = Virtual
