# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import os
import random

import pandas as pd
import xarray as xr
from tqdm import tqdm

import climetlab as cml

from .benchmarks.indexed_url import benchmark as benchmark_indexed_url
from .tools import experimental, parse_args

home = os.path.expanduser("~")

DATA_DATALOADING = {
    "grib": f"{home}/links/weather-bench-links/data-from-mc-symlinks-to-files-small/grib",
    "netcdf": f"{home}/links/weather-bench-links/data-from-ma/netcdf/pl_1999.nc",
    "b": f"{home}/dev/climetlab/tests/sources/gribs/b",
}


def benchmark_dataloading(*args):

    now = datetime.datetime.now

    class Exp:
        def __init__(self, directory):
            self.directory = directory

        def _get_selection(self):
            i_times = []
            dates = []
            n = int(args[2])  # number of dates to generate
            while len(i_times) < n:
                day = random.randint(1, 365)
                if day in i_times:
                    continue
                i_times.append(day)
                date = "1999" + pd.to_datetime(day, format="%j").strftime("%m%d")
                dates.append(date)
            assert len(dates) == n, (n, dates)
            print(dates)
            dates = sorted(dates)
            i_times = sorted(i_times)

            # dic = {"date": dates}
            dic = {"date": dates, "time": "0000"}
            # dic = {"date": dates, "time": "0000", "step": "0"}
            # dic = {"param":"z", "time": "0000", "step": "0"}
            # dic = {}
            # dic = {"date": "19990115"}
            # dic = {"date": ["19990115", "19990116"]}
            # dic = {"date": ["19990115", "19990116", "19990117", "19990118"]}
            return dic, dict(time=i_times)

    class GribExp(Exp):
        def get_ds(self):
            dic, isel_dic = self._get_selection()
            self.ds = cml.load_source("local", self.directory, dic)
            print(len(self.ds))

        def get_values(self):
            if args[1] == "direct":
                for one in tqdm(self.ds):
                    one.values.shape
                return

            elif args[1] == "xr":
                xds = self.ds.to_xarray()
                print(xds)
                for v in xds.variables:
                    print(v, xds[v].values.shape)
                return

            raise NotImplementedError()

    class NetcdfExp(Exp):
        def get_ds(self):
            self.ds = xr.open_dataset(self.directory)
            print(len(self.ds))

        def get_values(self):
            print(self.ds)

            dic, isel_dic = self._get_selection()
            ds = self.ds.isel(**isel_dic)

            for v in ds.variables:
                print(v, ds[v].values.shape)

    class ExpOnB(Exp):
        def _get_selection(self):
            return dict(param="2t", realization="0"), None

    def usage():
        print(
            """
        Usage:

        This script runs benchmark to get data, with two steps:
        1 - Get a handle on the dataset.
        2 - Then read the actual data.

        $0 grib direct 5:
        Read grib data with custom index.
        (Building climetlab.index json file if needed. Building .db in the database if needed.)
        Then read data directly asking eccode to decode the grib data.
        Using 5 dates.

        $0 grib xr 5:
        Same as above, but use to_xarray to read the data.
        This xarray calls cfgrib engine which calls climetlab which calls eccodes.

        $0 netcdf _ 5:
        Read the same data on netcdf files (second argument _ is a dummy argument) (TODO:yes, we need to use argparse).

        """
        )

    if len(args) == 0:
        usage()
        return

    d = args[0]
    d = DATA_DATALOADING.get(d, d)
    print(f"Using d={d}")

    if d.endswith(".nc") or d.endswith("netcdf"):
        exp = NetcdfExp(d)

    elif d.endswith("grib"):
        exp = GribExp(d)

    elif d.endswith("/b"):
        print("Todo fix this one")
        exp = ExpOnB(d)

    else:
        raise NotImplementedError()

    start = now()
    exp.get_ds()
    step_1 = now()
    exp.get_values()
    end = now()

    print("------------------")
    print("Time to get dataset handle:", step_1 - start)
    print("Time read the data from the dataset handle:", end - step_1)
    print("Total Time to actually read the data:", end - start)


class BenchmarkCmd:
    @parse_args(
        indexedurl=dict(
            action="store_true",
            help="Benchmark on using indexed URL (byte-range) and various servers.",
        ),
        dataloading=dict(
            action="store_true",
            help="Test loading some data.",
        ),
        nargs=dict(nargs="*"),
        all=dict(action="store_true", help="Run all benchmarks."),
    )
    @experimental
    def do_benchmark(self, args):
        """Run predefined benchmarks, for CliMetLab development purposes."""
        if args.all or args.indexedurl:
            print("Starting benchmark.")
            benchmark_indexed_url()

        if args.all or args.dataloading:
            print("Starting benchmark.")
            benchmark_dataloading(*args.nargs)
