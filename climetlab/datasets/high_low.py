# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import random

import numpy as np

from climetlab import load_source

from . import Dataset


def normalise_01(a):
    return (a - np.amin(a)) / (np.amax(a) - np.amin(a))


SAMPLES = [
    ("1993-04-08", (46.5, -118.5), (1.0, 0.0, 0.0, 0.0)),
    ("1993-04-08", (55.5, -15.0), (0.0, 0.0, 1.0, 0.0)),
    ("1993-04-08", (69.0, -52.5), (0.0, 1.0, 0.0, 0.0)),
    ("1993-04-09", (45.0, -106.5), (1.0, 0.0, 0.0, 0.0)),
    ("1993-04-09", (55.5, 142.5), (1.0, 0.0, 0.0, 0.0)),
    ("1993-04-09", (70.5, -49.5), (0.0, 1.0, 0.0, 0.0)),
    ("1993-04-09", (81.0, -82.5), (0.0, 1.0, 0.0, 0.0)),
    ("1993-04-10", (46.5, -94.5), (1.0, 0.0, 0.0, 0.0)),
    ("1993-04-10", (63.0, -75.0), (0.0, 0.0, 1.0, 0.0)),
    ("1993-04-10", (69.0, 58.5), (0.0, 0.0, 0.0, 1.0)),
    ("1993-04-10", (82.5, -6.0), (0.0, 0.0, 0.0, 1.0)),
    ("1993-04-12", (55.5, -130.5), (1.0, 0.0, 0.0, 0.0)),
    ("1993-04-12", (69.0, 63.0), (0.0, 0.0, 0.0, 1.0)),
    ("1993-04-12", (90.0, 70.5), (0.0, 1.0, 0.0, 0.0)),
    ("1993-04-13", (55.5, 150), (1.0, 0.0, 0.0, 0.0)),
    ("1993-04-13", (67.5, -55.5), (0.0, 0.0, 1.0, 0.0)),
    ("1993-04-15", (49.5, -109.5), (1.0, 0.0, 0.0, 0.0)),
    ("1993-04-15", (52.5, -90.0), (0.0, 0.0, 1.0, 0.0)),
    ("1993-04-15", (90.0, 75.0), (0.0, 1.0, 0.0, 0.0)),
    ("1993-04-18", (64.5, -45.0), (1.0, 0.0, 0.0, 0.0)),
    ("1993-04-18", (64.5, -64.5), (0.0, 0.0, 1.0, 0.0)),
    ("1993-04-18", (81.0, -139.5), (0.0, 0.0, 0.0, 1.0)),
    ("1993-04-20", (58.5, -153.0), (0.0, 1.0, 0.0, 0.0)),
    ("1993-04-20", (60.0, -30.0), (1.0, 0.0, 0.0, 0.0)),
    ("1993-04-20", (63.0, 109.5), (0.0, 0.0, 1.0, 0.0)),
    ("1993-04-20", (70.5, -7.5), (0.0, 0.0, 1.0, 0.0)),
    ("1993-04-21", (49.5, -105), (1.0, 0.0, 0.0, 0.0)),
    ("1993-04-21", (60, 64.5), (0.0, 0.0, 0.0, 1.0)),
    ("1993-04-21", (63.0, 0), (0.0, 0.0, 1.0, 0.0)),
    ("1993-04-21", (69.0, -51), (1.0, 0.0, 0.0, 0.0)),
    ("1993-04-22", (49.5, 160.5), (1.0, 0.0, 0.0, 0.0)),
    ("1993-04-22", (63.0, -60.0), (0.0, 0.0, 1.0, 0.0)),
    ("1993-04-22", (64.5, -60.0), (0.0, 0.0, 1.0, 0.0)),
    ("1993-04-22", (79.5, -90.0), (0.0, 1.0, 0.0, 0.0)),
    ("1993-04-22", (82.5, 85.5), (0.0, 0.0, 0.0, 1.0)),
    ("1993-04-26", (70.5, 0), (0.0, 0.0, 0.0, 1.0)),
    ("1993-04-26", (90, 153.5), (0.0, 0.0, 0.0, 1.0)),
]


class HighLow(Dataset):
    def __init__(self, **req):
        self._fields = []
        for date, area, label in SAMPLES:

            source = load_source(
                "cds",
                "reanalysis-era5-pressure-levels",
                variable="z",
                level=500,
                product_type="reanalysis",
                area=[area[0], area[1], area[0] - 30, area[1] + 30],
                date=date,
                grid=[1.5, 1.5],
                time=12,
            )

            for s in source:
                self._fields.append((s, label))
        self.source = source

    def fields(self):
        return self._fields

    def title(self, label):
        titles = ["Trough", "Low", "Ridge", "High"]
        i = np.argmax(label)
        if label[i] == 1.0:
            return titles[i]
        return "%s (%s%%)" % (titles[i], int(label[i] * 100 + 0.5))

    # load_data is used by keras
    def load_data(self, normalise=True, test_size=0.5, shuffle=True, fields=False):
        data = []
        for field, label in self._fields:
            if normalise:
                array = normalise_01(field.to_numpy())
            else:
                array = field.to_numpy()
            data.append((array, label, field))

        if shuffle:
            random.shuffle(data)
        half = int(len(data) * (1.0 - test_size))

        x_train, y_train, f_train = (
            np.array([x[0] for x in data[:half]]),
            np.array([x[1] for x in data[:half]]),
            [x[2] for x in data[:half]],
        )

        x_test, y_test, f_test = (
            np.array([x[0] for x in data[half:]]),
            np.array([x[1] for x in data[half:]]),
            [x[2] for x in data[half:]],
        )

        if fields:
            return (x_train, y_train, f_train), (x_test, y_test, f_test)

        return (x_train, y_train), (x_test, y_test)


dataset = HighLow
