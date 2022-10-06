#!/user/bin/env python3
# flake8: noqa
import os
import sys

import xarray as xr

import climetlab as cml
from climetlab.distributed.dask import start_dask


def build_sandbox(test_dir):
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, "grib"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "netcdf"), exist_ok=True)

    for i in [1, 2]:
        s = cml.load_source(
            "cds",
            "reanalysis-era5-single-levels",
            variable=["2t", "msl"],
            product_type="reanalysis",
            area=[50, -50, 20, 50],
            grid="10/10",
            date=f"2015-04-0{i}",
            time="12:00",
            format="netcdf",
        )
        s.save(os.path.join(test_dir, "netcdf", f"{i}.nc"))

    for i in [1, 2]:
        s = cml.load_source(
            "cds",
            "reanalysis-era5-single-levels",
            variable=["2t", "msl"],
            product_type="reanalysis",
            area=[50, -50, 20, 50],
            grid="10/10",
            date=f"2011-12-0{i}",
            time="12:00",
            format="grib",
        )
        s.save(os.path.join(test_dir, "grib", f"{i}.grib"))


def pprint(txt):
    logfile = f"/ec/res4/scratch/mafp/experiments/dask_tests/log/log.txt"
    with open(logfile, "a") as f:
        print(txt)
        print(txt, file=f)


client = None


def use(ds):
    ds.attrs = {}
    pprint("............. got metadata ......")
    pprint(ds)
    pprint("............. mean() ............")
    m = ds.mean()
    pprint("............. compute() .........")
    m = m.compute()
    pprint(float(m))
    # def f(x):
    #    return x + 1

    # global client
    # m = f(m)
    # a = client.compute(m)
    # print(a.result())
    pprint(".................................")


CHUNKS = dict(latitude=None, longitude=None, time=1)


def do_netcdf(testdir):
    ds = xr.open_mfdataset(os.path.join(testdir, "netcdf/*.nc"), chunks=CHUNKS)["msl"]
    use(ds)


def do_grib_mfdataset(testdir):
    # This is using cfgrib to index grib files (and create .idx) and provide data to xarray
    # The automatic merging does not work without more tweaks
    a = xr.open_mfdataset(os.path.join(testdir, "grib/1.grib"), chunks=CHUNKS)["msl"]
    b = xr.open_mfdataset(os.path.join(testdir, "grib/2.grib"), chunks=CHUNKS)["msl"]
    ds = xr.concat([a, b], dim="time")
    use(ds)


def do_grib_directory_source(testdir):
    # This is using climetlab to index the grib file
    # providing a unique grib-like object to xarray.open_dataset
    # Loading the data is using climetlab code Handler (calling eccodes anyways)
    s = cml.load_source("directory", os.path.join(testdir, "grib"), variable="msl")
    # beware: ds = s.to_xarray()['msl'] would load everything in memory.
    ds = s.to_xarray(xarray_open_dataset_kwargs=dict(chunks=CHUNKS))["msl"]
    use(ds)


def do_virtual():
    s = cml.load_source("virtual")
    ds = s.to_xarray()["t2m"]
    use(ds)


def main():
    # global client
    task = None
    if len(sys.argv) > 1:
        task = sys.argv[1]
    testdir = "sandbox"
    start_dask("slurm")
    # start('ssh', ['localhost)

    if task == "nc":
        build_sandbox(testdir)
        do_netcdf(testdir)
        return
    if task == "grib-openmf":
        build_sandbox(testdir)
        do_grib_mfdataset(testdir)
        return
    if task == "virtual":
        do_virtual()
        return
    do_grib_directory_source(testdir)


if __name__ == "__main__":
    main()
