def post_xarray_open_dataset_hook(ds):
    # we may want to do this too :
    # import cf2cdm
    # ds = cf2cdm.translate_coords(ds, cf2cdm.CDS)
    # or
    # ds = cf2cdm.translate_coords(ds, cf2cdm.ECMWF)

    # ensure our internal conventions
    if "number" in list(ds.coords):
        ds = ds.rename({"number": "realization"})
    if "time" in list(ds.coords):
        ds = ds.rename({"time": "forecast_time"})
    if "valid_time" in list(ds.coords):
        ds = ds.rename({"valid_time": "time"})
    if "heightAboveGround" in list(ds.coords):
        # if we decide to keep it, rename it.
        # ds = ds.rename({'heightAboveGround':'height_above_ground'})
        ds = ds.squeeze("heightAboveGround")
        ds = ds.drop("heightAboveGround")
    if "surface" in list(ds.coords):
        ds = ds.squeeze("surface")
        ds = ds.drop("surface")
    return ds


def open_dataset_params(time_convention="withstep"):
    params = {}
    if time_convention == "withstep":
        time_dims = ["time", "step"]  # this is the default of engine='cfgrib'
        chunk_sizes_in = {
            "time": 1,
            "latitude": None,
            "longitude": None,
            "number": 1,
            "step": 1,
        }

    elif time_convention == "nostep":
        time_dims = ["time", "valid_time"]
        chunk_sizes_in = {
            "time": 1,
            "latitude": None,
            "longitude": None,
            "number": 1,
            "valid_time": 1,
        }

    else:
        raise Exception()

    # params['engine'] = 'cfgrib'
    params["chunks"] = chunk_sizes_in
    params["backend_kwargs"] = dict(squeeze=False, time_dims=time_dims)

    return params
