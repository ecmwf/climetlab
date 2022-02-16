import xarray as xr

import climetlab as cml


def test_grib_index_eumetnet():
    from climetlab import load_source
    from climetlab.indexing import PerUrlIndex

    request = {
        "param": "2ti",
        "date": "20171228",
        "step": ["0-24", "24-48", "48-72", "72-96", "96-120", "120-144", "144-168"],
        # Parameters passed to the filename mangling
        "url": "https://storage.ecmwf.europeanweather.cloud/eumetnet-postprocessing-benchmark-training-dataset/",
        "month": "12",
        "year": "2017",
    }
    PATTERN = "{url}data/fcs/efi/" "EU_forecast_efi_params_{year}-{month}_0.grb"
    ds = load_source("indexed-urls", PerUrlIndex(PATTERN), request)
    xds = ds.to_xarray()
    print(xds)


test_grib_index_eumetnet()
