# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

AREAS = {
    "austria": (55.5, 6.0, 40.0, 21.5),
    "azores": (46.0, -35.0, 30.5, -19.5),
    "balearic islands": (47.5, -4.5, 32.0, 11.0),
    "belgium": (58.5, -3.0, 43.0, 12.5),
    "bulgaria": (50.5, 18.0, 35.0, 33.5),
    "canary islands": (36.5, -23.0, 21.0, -7.5),
    "corsica": (50.0, 1.5, 34.5, 17.0),
    "croatia": (52.5, 9.0, 37.0, 24.5),
    "czech republic": (58.0, 8.0, 42.5, 23.5),
    "denmark": (64.0, 3.0, 48.5, 18.5),
    "estonia": (66.5, 17.5, 51.0, 33.0),
    "finland": (73.0, 18.5, 57.5, 34.0),
    "france": (54.5, -6.0, 39.0, 9.5),
    "germany": (59.0, 3.0, 43.5, 18.5),
    "greece": (46.5, 16.5, 31.0, 32.0),
    "hungary": (55.0, 12.0, 39.5, 27.5),
    "iceland": (73.0, -26.0, 57.5, -10.5),
    "ireland": (61.5, -15.0, 46.0, 0.5),
    "israel": (39.5, 27.5, 24.0, 43.0),
    "italy": (50.5, 5.0, 35.0, 20.5),
    "latvia": (65.0, 17.0, 49.5, 32.5),
    "lithuania": (63.0, 16.5, 47.5, 32.0),
    "luxembourg": (58.0, -1.5, 42.5, 14.0),
    "madeira": (41.0, -24.0, 25.5, -8.5),
    "montenegro": (50.5, 12.0, 35.0, 27.5),
    "morocco": (36.5, -16.0, 21.0, -0.5),
    "netherlands": (60.0, -2.5, 44.5, 13.0),
    "north macedonia": (49.5, 14.0, 34.0, 29.5),
    "norway": (73.0, 4.5, 57.5, 20.0),
    "portugal": (47.5, -15.0, 32.0, 0.5),
    "republic of serbia": (52.0, 13.5, 36.5, 29.0),
    "romania": (54.0, 17.5, 38.5, 33.0),
    "sardinia": (48.0, 1.5, 32.5, 17.0),
    "sicily": (45.5, 6.5, 30.0, 22.0),
    "slovakia": (56.5, 12.0, 41.0, 27.5),
    "slovenia": (54.0, 7.5, 38.5, 23.0),
    "spain": (48.0, -10.0, 32.5, 5.5),
    "sweden": (70.0, 10.0, 54.5, 25.5),
    "switzerland": (55.0, 0.5, 39.5, 16.0),
    "turkey": (47.0, 25.5, 31.5, 41.0),
    "united kingdom": (63.5, -10.0, 48.0, 5.5),
}

AREAS["uk"] = AREAS["united kingdom"]
AREAS["serbia"] = AREAS["republic of serbia"]


def domain_to_area(name):
    if isinstance(name, (list, tuple)):
        return name
    return AREAS[name.lower()]
