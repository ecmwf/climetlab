import pandas as pd
import numpy as np
import xarray as xr

data = np.random.rand(4, 3)

locs = ["IA", "IL", "IN"]

times = pd.date_range("2000-01-01", periods=4)

foo = xr.DataArray(data, coords=[times, locs], dims=["time", "space"])

foo.attrs["_climetlab"] = 2
print(foo)

bar = foo.to_dataset(name="foo")
bar.attrs["_climetlab"] = 3

print(bar)
