import climetlab as clm

ds = clm.load_dataset("meteonet-masks")


print(ds.to_xarray())
