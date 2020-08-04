# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from . import Dataset
from climetlab.utils.domains import domain_to_area
from climetlab import load_source


class Era5SingleLevels(Dataset):
    def __init__(self, variable, period, domain=None, time=None, grid=None):

        request = dict(variable=variable, product_type="reanalysis",)

        if domain is not None:
            request["area"] = domain_to_area(domain)

        if time is not None:
            request["time"] = time

        if grid is not None:
            if isinstance(grid, (int, float)):
                request["grid"] = [grid, grid]
            else:
                request["grid"] = grid

        sources = []
        for year in range(period[0], period[1] + 1):
            request["year"] = year
            sources.append(
                load_source("cds", "reanalysis-era5-single-levels", **request)
            )

        self.source = load_source("multi", sources)


dataset = Era5SingleLevels
