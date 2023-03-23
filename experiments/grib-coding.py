import os

import numpy as np

import climetlab as cml
import climetlab.debug

f = cml.new_grib_output("test.grib")

f.write(
    np.random.rand(181, 360),
    metadata=dict(
        param="msl",
        date="1990-01-01T12:00",
        expver="xxxx",
    ),
)

print(os.path.getsize("test.grib"))


f = cml.new_grib_output("test2.grib")

f.write(
    np.random.rand(180 * 2, 360 * 2),
    metadata=dict(
        param="msl",
        date="1990-01-01T12:00",
        expver="xxxx",
    ),
)

print(os.path.getsize("test2.grib"))

f = cml.new_grib_output("test3.grib")

f.write(
    np.random.rand(40320),
    metadata=dict(
        param="msl",
        date="1990-01-01T12:00",
        expver="xxxx",
    ),
)

print(os.path.getsize("test3.grib"))
