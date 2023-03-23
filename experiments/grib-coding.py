import os

import np

import climetlab as cml
import climetlab.debug

f = cml.new_grib_output("test.grib")

f.write(
    np.random.rand((181, 360)),
    metadata=dict(
        param="msl",
        date="1990- 01-01T12:00",
        expver="xxxx",
    ),
)

print(os.path.getsize("test.grib"))
