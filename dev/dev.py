import xarray as xr

import climetlab as cml


def build_netcdf():
    from climetlab import load_source

    source = load_source(
        "dummy-source",
        kind="netcdf",
        dims=["lat", "lon"],
    )
    ds = source.to_xarray()
    ds.to_netcdf("test.nc")


build_netcdf()


ds = xr.open_dataset("test.nc")
print(ds)

# works on linux,  fails on windows
cml.plot_map(ds, path="test.png")
