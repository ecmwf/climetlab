import numpy as np

import climetlab as cml

# cmlds = cml.load_source("indexed-directory", "/lus/h2resw01/fws4/lb/project/ai-ml/test")
cmlds = cml.load_source(
    "indexed-directory",
    "/lus/h2resw01/fws4/lb/project/ai-ml/era5-for-ai",
    # datetime=['date', 'time']
    # datetime=['valid_date + valid_time']
)
cmlds = cmlds.sel(date=[19790501, 19790502])
# cmlds = cml.load_source("indexed-directory", "testdir")

ds = cmlds.sel(levtype="pl")

print(ds)


print()
cube = ds.cube("date", "time", "param", "levelist")
print(cube)

assert cube.shape == (2, 4, 6, 37), cube.shape

assert cube[:, 1, 1, :].shape == (2, 37)
assert cube[0, 1, 1, :].shape == (37,)
assert cube[1, 1:2, :].shape == (1, 6, 37)
assert cube[1, :, :, :].shape == (4, 6, 37)
assert cube[1, :].shape == (4, 6, 37)
assert cube[1, ...].shape == (4, 6, 37)

f = cube[1, 3, 5, 36]
assert f.metadata("date") == 19790502, f
assert f.metadata("time") == 1800, f
assert f.metadata("param") == "z", f
assert f.to_numpy().shape == (721, 1440), f

f = cube[1, 2, 4, 15]
assert f.metadata("date") == 19790502, f
assert f.metadata("time") == 1200, f
assert f.metadata("param") == "w", f
assert f.to_numpy().shape == (721, 1440), f


def f(year, param_level, time):
    # implicit: all date in the year
    assert isinstance(year, int)
    assert isinstance(param_level, (list, tuple))  # all str
    assert isinstance(time, (list, tuple))  # all str
    assert time[0] == "00:00"
    assert time[1] == "06:00"
    assert time[2] == "12:00"
    assert time[3] == "18:00"

    ###

    arr = np.array()
    assert arr.shape(20, 365, 4, 721, 1440)

    assert arr.shape(20 * 37, 365, 4, 721, 1440)
    return arr
