#!/usr/bin/env python3
import climetlab as cml
import Magics
from climetlab.core.bbox import BoundingBox
from Magics import macro

bbox = BoundingBox(north=90, west=0, east=360, south=-90)

cml.plot_map(bounding_box=bbox, projection="polar-north", path="x.png")
