# import entrypoints


# for e in entrypoints.get_group_all('climetlab.datasets'):
#     print(e)
#     print(e.load())

from climetlab import load_dataset

ds = load_dataset("demo-dataset")
print(ds)
