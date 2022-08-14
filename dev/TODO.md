
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

** Jupyter

- Check _ipython_key_completions_
- Use jsonschemo.org for magics
- See https://github.com/readthedocs/sphinx-autoapi

** Doc
- Check external links https://sublime-and-sphinx-guide.readthedocs.io/en/latest/references.html


Check
https://snakemake.readthedocs.io/en/stable/tutorial/basics.html

Jupyter
paperspace.com


# API discussion (working document)

xr.open_dataset('climetlab:s2s-ai-competition/training', date=. , origin=.)
pd.open_climetlab('climetlab:s2s-ai-competition/training', date=. , origin=.)

ds = cml.open_dataset(name='s2s-ai-competition/training', origin=.)
ds.to_xarray()

cml.open_dataset(name='s2s-ai-competition/training', date=. , origin=., as_type=pd.DataFrame, format=., select_kwargs={})
is a shortcut for
cml.Dataset('s2s-ai-competition','training', format=.).select_or(date=. , origin=.).to_pandas()

cml.Dataset('s2s-ai-competition','training', format='grib', debug=True).select_or(format='%02d', debug=True, date=. , origin=.).to_pandas()

 in_init = ['format']
 def __init__(self, format, **kwargs):
 in_select(self, date, origin, **kwargs):

--------------
## Defining the dataset : cml.Dataset

ds1 = cml.Dataset('s2s-ai-competition', 'training', format='grib')
ds2 = cml.Dataset('s2s-ai-competition', 'training', format='netcdf')
ds3 = cml.Dataset('s2s-ai-competition', 'training', format='netcdf', mirror='s3://my-renku-s3/')
 ds1 and ds2 and ds3 refer to the same data, but different format/location. ds.to_xarray() will provide the same thing.
 The first string "s2s-ai-competion" is from the plugin name : "climetlab-s2s-ai-competition" : you know which plugin you need to install.
 The second string defines the actual dataset name.

? ds = cml.Dataset('s2s-ai-competition/training', format='grib')
Not documented : cml.dataset('s2s-ai-competition', subset='training')

ds = cml.Dataset('s2s-ai-competition', 'training') default format='grib', default location.
ds = cml.Dataset('s2s-ai-competition')  # default format='grib', default location + default dataset (training-ecmwf) OR # Exception missing parameter "datasetname".

? cml.s2s_ai_competition('training-cwao')
? climetlab_s2s_ai_competition.dataset('training-cwao')

No http request in __init__ to get anything (data or metadata).

? Change format/location ?
? ds.reset_dataset(format='grib')

--------------
## Metadata/info/availability/citation/homepage : attributes of Dataset() object.

 list all dataset provided but the plugin (in the family)
ds = cml.Dataset('s2s-ai-competition', '*')
ds.info

ds = cml.Dataset('meteonet')
ds.info
 -> list all datasets
 -> citation, homepage, etc for meteonet

ds = cml.Dataset('meteonet', 'radar')
ds.info
 -> availability
 -> citation, homepage, etc for meteonet-radar data
ds.availability
ds.citation
ds.homepage

--------------
## Filter/select the data : ds.find_a_name(...)

ds.load(date=., origin=.)
ds.select_or(date=., origin=.)
ds.select_and(date=., origin=.)

--------------
## Get the data as xarray or panda or grib, lazily if possible.

ds.to_xarray()
Zarr : lazzily get the data.
Grib : create a lazzy xarray from the .availability ?
ds.to_pandas()
Do not use ds.astype


## other ideas
ds = cml.Dataset('meteonet', plugin='climetlab-meteonet')
ds = cml.Dataset('meteonet', plugin='intake-meteonet')


## LOOK AT

https://pypi.org/project/lazy-object-proxy/
https://wrapt.readthedocs.io/en/latest/wrappers.html#object-proxy
