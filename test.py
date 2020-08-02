import climetlab as clm

ds = clm.load_dataset("meteonet-radar")


print(ds.to_xarray())
