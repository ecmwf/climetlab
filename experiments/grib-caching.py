# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
# flake8: noqa


from climetlab import load_source
from climetlab.profiling import timer

years = list(range(1979, 2021))
years = list(range(1979, 1979 + 3))


with timer("load_source"):
    s = load_source(
        "cds",
        "reanalysis-era5-single-levels-monthly-means",
        variable="all",
        year=years,
        month=list(range(1, 13)),
        time=0,
        product_type="monthly_averaged_reanalysis",
        # grid=[0.25, 0.25],
        grid=[1, 1],
        split_on="year",
    )

with timer("len"):
    print(len(s))
