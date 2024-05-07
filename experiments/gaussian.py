# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
# flake8: noqa

import time

import climetlab as cml
from climetlab.grids import lookup
from climetlab.grids import unstructed_to_structed

ds = cml.load_source("mars", param="2t", date=20220907, levtype="sfc")
tree = unstructed_to_structed(ds[0], 15)

now = time.time()
print(lookup(tree, 51.0, -1.0))
print("----", time.time() - now)
