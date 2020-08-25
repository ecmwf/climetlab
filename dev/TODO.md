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

##


# Bug fixes

## BUFR

- Return NaN instead of -1e+100

## Magics

- Get stuck if geopoints is empty

