import os

import climetlab as cml
import climetlab.debug

p = cml.load_source("mars", grid=[1, 1])
print(p[0].shape)
# print(p[0].metadata())

f = cml.new_grib_output("test.grib")

data = p[0].to_numpy()
f.write(
    data,
    metadata=dict(
        param="msl",
        # time=12,
        date="1990-01-01T12:00",
        step=12,
        number=1,
    ),
)

print(os.path.getsize("test.grib"))
