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
import pyfdb
LOG = logging.getLogger(__name__)


class NoLock:
    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass



class FDB(GribIndex):
    SIZE = int(365.25 * 24 * (2022 - 1959))
    # SIZE = 100

    DATASET = dict(
        dataset="reanalysis-era5-single-levels",
        product_type="reanalysis",
        param="msl",
        grid="10/10",
    )

    def __init__(self, request):
        super().__init__()
        for n in pyfdb.list(request):
            print(n)

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




source = FDB
