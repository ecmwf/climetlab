
# Features

## Cache management

- Allow user to force download of cached datasets

## Sources requests

Option1, will get area/date/time based on what is in `frame`. Controlled by the
options

```python
frame = foo.to_pandas()

s = cml.load_source("cds", "era5-single-level",
    param='msl',
    based_on = {"data": frame, "option1": "...", "option2": "..."}
    )
```

Option2, more direct approach, gets the bounding box from `frame`

```python
frame = foo.to_pandas()

s = cml.load_source("cds", "era5-single-level",
    param='msl',
    area = frame,
    date = frame,
    )
```

Option3, `frame` will generate a valid request. Issue: different requests for different sources

```python
frame = foo.to_pandas()

s = cml.load_source("cds", "era5-single-level",
    param='msl',
    **frame.to_request(...)
    )
```

Option4, using help function

```python
frame = foo.to_pandas()

s = cml.load_source("cds", "era5-single-level",
    param='msl',
    area=cml.get_bounding_box(frame),
    date=cml.get_dates(frame)
    )
```

## Datasets

## Data sources

## Magics

- Plot CSV files (as geopoints)
- If netcdf_dimension_setting is empty, error

## Settings

Implement settings

# Bug fixes

## BUFR

- Return NaN instead of -1e+100

## Magics

- Get stuck if geopoints is empty
- Netcdf don't plot if lat/long integers
- Netcdf don't plot if dimensions=[]
- Magics-ERROR: NetcdfDecoder : No accessor available for 10
libc++abi.dylib: terminating with uncaught exception of type magics::MagicsException*

# Stuff

## Settings for vscode

```bash
"python.dataScience.runStartupCommands": ["%load_ext autoreload", "%autoreload 2"]
```

## IPython

See <https://ipython.readthedocs.io/en/stable/config/integrating.html>

## RST

Use `doc8` instead of `rstcheck`

## Packages of interest

- <https://pypi.org/project/docstring-expander/>


# Tasks

- Collect use cases
- Work on caching
  - Use sqlite
  - Expiry
  - Size limit
  - Location
- Work on settings
- Work on the definition of datasets in YAML
- Documentation
- Decisions regarding plotting
- YAML files for:
  - Styles
  - Projections
- Windows version
- New magics
- Code of conduct
- Identify data sources
- Identify datasets
- Deploy on Jupyter Hub
- Add unit tests
- Investigate
  - intake
  - zarr
  - dask
- Introduce catalogues
  - cml.add_catalog (catalogue)
- Iterators?
  - plot_map(d) vs plot_map(d[0])
- CI/CD

** Jupyter

- Check _ipython_key_completions_
- Use jsonschemo.org for magics
- See https://github.com/readthedocs/sphinx-autoapi
