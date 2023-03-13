import climetlab as cml

# cmlds = cml.load_source("indexed-directory", "/lus/h2resw01/fws4/lb/project/ai-ml/test")
cmlds = cml.load_source("indexed-directory", "/lus/h2resw01/fws4/lb/project/ai-ml/era5-for-ai").sel(date=19790501)
#cmlds = cml.load_source("indexed-directory", "testdir")



for dic in [
    dict(param="t"),
    dict(param_level="t_500"),
    dict(level=500),
]:
    print(dic)
    ds = cmlds.sel(**dic)
    print(ds.availability)


exit()

# cube = ds.cube(param=[...], time=[...], level=[...])
# cube['2t',3:5,:].to_numpy()


import sys

import pandas as pd
import tqdm

import climetlab as cml
from climetlab.decorators import normalize

ALL_DATES = pd.date_range(start="1980-01-01", end="1980-01-03", freq="1d")


@normalize("x", values=ALL_DATES, type="date")
def go(x):
    print(x, type(x))


go(5)
exit()

DIR = "/lus/h2resw01/fws4/lb/project/ai-ml/graph-cast/pl-no-param-level"

DATE = ["20000101", "20000102"]
FEATURES = ["z_500", "t_850"]

if len(sys.argv) > 1:
    if sys.argv[1] == "large":
        DATE = pd.date_range(start="1980-01-01", end="2020-12-31", freq="1d")
        FEATURES = [
            f"{param}_{pl}"
            for param in ["q", "t", "u", "v", "w", "z"]
            for pl in [1, 10, 100, 1000, 125, 150, 175, 2, 20]
            + [200, 225, 250, 3, 30, 300, 350, 400, 450, 5, 50, 500, 550]
            + [600, 650, 7, 70, 700, 750, 775, 800, 825, 850, 875, 900, 925, 950, 975]
        ]
        # FEATURE += ['10u', '10v', '2t', 'msl', 'tp'] # not indexed in the same directory for now.
    if sys.argv[1] == "medium":
        # DATE = pd.date_range(start="1980-01-01", end= "2020-12-31", freq ='1d')
        DATE = pd.date_range(start="2000-01-01", end="2000-12-31", freq="1d")
        FEATURES = [
            f"{param}_{pl}"
            for param in ["q", "t", "u", "v", "w", "z"]
            for pl in [100, 1000, 200, 300, 400, 500, 600, 700, 750, 800, 850, 900, 950]
        ]


ds = cml.load_source("directory", DIR, date=DATE)
ds = ds.order_by("date", "time")  # "param", "level")

# TODO: ds = ds.order_by('date', 'time', 'batch', 'param', 'level')
# TODO: ds = ds.order_by('date', 'time', 'batch', 'space', 'param', 'level')


def build(data, names):
    lst = []
    size = None
    for f in tqdm.tqdm(names):
        # z500 = ds.sel(param_level=f)
        if "_" in f:
            param, level = f.split("_")
            elt = data.sel(param=param, level=int(level))
        else:
            elt = data.sel(param=f)

        if size is None:
            size = len(elt)
        assert len(elt) == size, f"wrong size for feature {f}"

        lst.append(elt)
    return lst


features = build(ds, FEATURES)
targets = build(ds, FEATURES)
# targets = build(ds, ['z_500'])
print(len(features), "features ready")
print(len(targets), "targets ready")

kwargs = dict(features=features, targets=targets)

## torch dataset
# from climetlab.readers.grib.pytorch import to_pytorch
# dataset = to_pytorch(**kwargs)
dataset = features[0].to_pytorch(**kwargs)
# print("created pytorch dataset", dataset, type(dataset))
# for i, xy in enumerate(tqdm.tqdm(dataset, smoothing=1)):
#    x, y = xy
#    print(i, x.shape, y.shape, type(x))


## torch dataloader
# dataloader = features[0].to_pytorch_dataloader(**kwargs)
from climetlab.readers.grib.pytorch import to_pytorch_dataloader

dataloader = to_pytorch_dataloader(dataset, batch_size=2, num_workers=8)
print("created pytorch dataloader", dataloader)
for x, y in tqdm.tqdm(dataloader, smoothing=1):
    print(x.shape, y.shape, type(x))
    x.cuda(), y.cuda()
