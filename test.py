#!/usr/bin/env python3
import Magics
from Magics import macro

import climetlab as cml
from climetlab.core.bbox import BoundingBox

bbox = BoundingBox(north=90, west=0, east=360, south=-90)

cml.plot_map(bounding_box=bbox, projection="polar-north", path="x.png")
