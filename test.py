from climetlab import load_source

source = load_source(
    "cds",
    "reanalysis-era5-single-levels",
    variable=["2t", "msl"],
    product_type="reanalysis",
    area=[50, -50, 20, 50],
    date="2012-12-12",
    time="12:00",
)


# url = "https://storage.ecmwf.europeanweather.cloud/s2s-ai-competition/data/zarr/2t.zarr"

# ds = load_source("zarr-s3", url)
# print(ds)
# print(ds.to_xarray())
