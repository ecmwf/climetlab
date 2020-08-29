# import entrypoints


# for e in entrypoints.get_group_all('climetlab.datasets'):
#     print(e)
#     print(e.load())

from climetlab import load_dataset, plot_map

ds1 = load_dataset("sample-bufr-data")
ds2 = load_dataset("sample-bufr-data")

plot_map((ds1, ds2))
