# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#


class PandasHelper:
    def __init__(self, frame, margins=0, column=None, **kwargs):

        self.frame = frame
        self.kwargs = kwargs
        self.margins = margins
        self.column = column

        if "lat@hdr" in self.frame:
            self.lat = "lat@hdr"
            self.lon = "lon@hdr"
        elif "lat" in self.frame:
            self.lat = "lat"
            self.lon = "lon"
        else:
            self.lat = "latitude"
            self.lon = "longitude"

    def plot_map(self, driver):

        north = self.frame[self.lat].max()
        south = self.frame[self.lat].min()

        lons1 = self.frame[self.lon]
        east1 = lons1.max()
        west1 = lons1.min()

        lons2 = self.frame[self.lon] % 360
        east2 = lons2.max()
        west2 = lons2.min()

        if abs(east1 - west1) <= abs(east2 - west2):
            east, west = east1, west1
        else:
            east, west = east2, west2

        driver.bounding_box(
            north=north + self.margins,
            south=south - self.margins,
            west=west - self.margins,
            east=east + self.margins,
        )

        if self.column is None:
            column = self.lat
        else:
            column = self.column

        path = driver.temp_file(".csv")
        with open(path, "w") as f:
            seen = set()

            for index, row in self.frame[[self.lat, self.lon, column]].iterrows():
                if (row[0], row[1]) not in seen:
                    print(",".join(str(x) for x in row), file=f)
                    if not self.column:
                        seen.add((row[0], row[1]))

        driver.plot_csv(path, column)
        driver.apply_kwargs(self.kwargs)

    def bounding_box(self):

        north, east = self.frame[[self.lat, self.lon]].max()
        south, west = self.frame[[self.lat, self.lon]].min()

        return [
            north + self.margins,
            west - self.margins,
            south - self.margins,
            east + self.margins,
        ]

    def dates(self):
        return sorted(set([str(x).split("T")[0] for x in self.frame["time"].values]))


helper = PandasHelper
