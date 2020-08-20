# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#


class PandasHelper:
    def __init__(self, frame, margins=0, **kwargs):

        self.frame = frame
        self.kwargs = kwargs
        self.margins = margins

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

        north, east = self.frame[[self.lat, self.lon]].max()
        south, west = self.frame[[self.lat, self.lon]].min()

        driver.bounding_box(
            north=north + self.margins,
            south=south - self.margins,
            west=west - self.margins,
            east=east + self.margins,
        )

        path = "tmp.geo"
        # driver.plot_grib(self.path, self.handle.get('offset'))
        with open(path, "w") as f:
            print("#GEO", file=f)
            print("#lat long value", file=f)
            print("#DATA", file=f)

            seen = set()

            for index, row in self.frame[[self.lat, self.lon]].iterrows():
                if (row[0], row[1]) not in seen:
                    print(row[0], row[1], 42.0, file=f)
                    seen.add((row[0], row[1]))

            # print("----", len(seen))

        driver.plot_geopoints(path)
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
