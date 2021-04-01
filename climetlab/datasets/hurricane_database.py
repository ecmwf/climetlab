# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# See https://www.aoml.noaa.gov/hrd/hurdat/Data_Storm.html

import functools

import numpy as np
import pandas as pd

from climetlab.utils import download_and_cache
from climetlab.utils.dates import parse_date

from . import Dataset

SIGN = {"N": 1, "W": -1, "E": 1, "S": -1}

TYPE = {
    "C": "Closest approach to a coast, not followed by a landfall",
    "G": "Genesis",
    "I": "An intensity peak in terms of both pressure and wind",
    "L": "Landfall (center of system crossing a coastline)",
    "P": "Minimum in central pressure",
    "R": "Provides additional detail on the intensity of the cyclone when rapid changes are underway",
    "S": "Change of status of the system",
    "T": "Provides additional detail on the track (position) of the cyclone",
    "W": "Maximum sustained wind speed",
}

STATUS = {
    "TD": "Tropical cyclone of tropical depression intensity (< 34 knots)",
    "TS": "Tropical cyclone of tropical storm intensity (34-63 knots)",
    "HU": "Tropical cyclone of hurricane intensity (> 64 knots)",
    "EX": "Extratropical cyclone (of any intensity)",
    "SD": "Subtropical cyclone of subtropical depression intensity (< 34 knots)",
    "SS": "Subtropical cyclone of subtropical storm intensity (> 34 knots)",
    "LO": (
        "A low that is neither a tropical cyclone, a subtropical cyclone,"
        " nor an extratropical cyclone (of any intensity)"
    ),
    "WV": "Tropical Wave (of any intensity)",
    "DB": "Disturbance (of any intensity)",
}


# https://en.wikipedia.org/wiki/Saffir–Simpson_scale
def category(knots):

    if knots < 83:
        return 1

    if knots < 96:
        return 2

    if knots < 113:
        return 3

    if knots < 137:
        return 4

    return 5


URLS = {
    "atlantic": "https://www.aoml.noaa.gov/hrd/hurdat/hurdat2.txt",
    "pacific": "https://www.aoml.noaa.gov/hrd/hurdat/hurdat2-nepac.html",
}


class HurricaneDatabase(Dataset):

    home_page = "https://www.aoml.noaa.gov/hrd/hurdat/Data_Storm.html"

    def __init__(self, *, bassin="atlantic", url=None):

        if url is None:
            url = URLS[bassin.lower()]

        path = download_and_cache(url)
        p = []
        with open(path) as f:
            lines = f
            for line in lines:
                if line[0] in (" ", "<", "\n"):
                    continue

                bassin = line[0:2]
                number = int(line[2:4])
                year = int(line[4:8])
                name = line[18:28].strip().lower()
                # id = line[0:8]

                # http://www.aoml.noaa.gov/hrd/hurdat/hurdat2-format-may2015.pdf

                for _ in range(0, int(line[33:36])):
                    line = next(lines)
                    knots = float(line[38:41])
                    pressure = np.NaN if line[43] == "-" else float(line[43:47])
                    time = "%s-%s-%sZ%s:%s" % (
                        line[0:4],
                        line[4:6],
                        line[6:8],
                        line[10:12],
                        line[12:14],
                    )
                    p.append(
                        dict(
                            # id=id,
                            bassin=bassin,
                            number=number,
                            year=year,
                            name=name,
                            time=parse_date(time),
                            type=line[16],
                            status=line[19:21],
                            lat=float(line[23:27]) * SIGN[line[27]],
                            lon=float(line[30:35]) * SIGN[line[35]],
                            knots=knots,
                            category=category(knots),
                            pressure=pressure,
                        )
                    )

        self.cyclones = self.annotate(pd.DataFrame(p), style="cyclone-track")

    def to_pandas(self, **kwargs):
        if kwargs:
            df = self.cyclones
            f = [df[k] == v for k, v in kwargs.items()]
            return df[functools.reduce(lambda a, b: a & b, f)]
        return self.cyclones


dataset = HurricaneDatabase
