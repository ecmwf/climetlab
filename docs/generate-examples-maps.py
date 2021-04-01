#!/usr/bin/env python3
# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

me = os.path.basename(__file__)
here = os.path.dirname(__file__)

CODE = """
import climetlab as cml
cml.plotting_options(path="{}")
{}
"""

for root, _, files in os.walk(here):
    for file in files:
        if file.endswith(".py") and file != me:
            full = os.path.join(root, file)
            with open(full) as f:
                code = f.read()
                if "plot_map" in code:
                    n = len(here) + 1
                    path = os.path.join(here, "_static", full[n:])
                    path = path.replace(".py", ".svg")
                    if not os.path.exists(os.path.dirname(path)):
                        os.makedirs(os.path.dirname(path))
                    print("PATH", path)
                    code = CODE.format(path, code)
                    exec(code, dict(__file__=full), {})
