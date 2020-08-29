import xarray as xr
import numpy as np
from climetlab import plot_map
import math

lon = np.arange(-180, 180, 1.0)
lat = np.arange(90, -91, -1.0)
t2m = np.zeros(shape=(len(lat), len(lon)))

for i in range(0, 181):
    for j in range(0, 360):
        t2m[i, j] = 273.15 + math.sin(i) + math.cos(j)

ds = xr.Dataset(
    {"t2m": (["latitude", "longitude"], t2m),},
    coords={"longitude": lon, "latitude": lat,},
)

ds["latitude"].attrs = dict(units="degrees_north", standard_name="latitude")
ds["longitude"].attrs = dict(units="degrees_north", standard_name="longitude")
ds["t2m"].attrs = dict(units="K", long_name="2 metre temperature")

print(ds)
plot_map(ds)
