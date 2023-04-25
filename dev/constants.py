import datetime

import climetlab as cml

sample = cml.load_source(
    "mars",
    levtype="sfc",
    param="2t",
    grid="O96",
    time=1200,
    date=20010101,
)


start = sample[0].datetime()
first_step = 6
last_step = 240
step_increment = 6
dates = []
for step in range(first_step, last_step + step_increment, step_increment):
    dates.append(start + datetime.timedelta(hours=step))


params = [
    "cos_latitude",
    "cos_longitude",
    "sin_latitude",
    "sin_longitude",
    "cos_julian_day",
    "cos_local_time",
    "sin_julian_day",
    "sin_local_time",
    "insolation",
]

ds = cml.load_source(
    "constants",
    sample,
    date=dates,
    param=params,
)


for f in ds:
    print(f)

assert len(ds) == len(params) * len(dates)
