import climetlab as clm

ds = clm.load_dataset("high-low")


print(ds.to_xarray())
