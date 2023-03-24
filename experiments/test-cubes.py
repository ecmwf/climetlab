import climetlab as cml

# import climetlab.debug  # noqa

t850 = cml.load_source("mars", param="t", level=850, grid=[1, 1], time=[1200, 1800])
z500 = cml.load_source("mars", param="z", level=500, grid=[1, 1], time=[1200, 1800])

ds = cml.load_source("multi", t850, z500)
ds = ds.full("param", "levelist")
print(len(ds))

for i in range(len(ds)):
    try:
        print("---", ds[i])
    except Exception as e:
        print(e)

############

ds = cml.load_source("multi", t850, z500)
c = ds.cube("time", "param+levelist")
# print(c)
print(c[0])
print(c[1])
