# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#


class PandasPlotter:
    def __init__(self, frame):
        self.frame = frame
        self.lat = "lat"
        self.lon = "lon"

    def plot_map(self, driver):
        north, east = self.frame[[self.lat, self.lon]].max()
        south, west = self.frame[[self.lat, self.lon]].min()
        driver.bounding_box(north=north, south=south, west=west, east=east)

        path = "tmp.geo"
        # driver.plot_grib(self.path, self.handle.get('offset'))
        with open(path, "w") as f:
            print("#GEO", file=f)
            print("#lat long value", file=f)
            print("#DATA", file=f)

            for index, row in self.frame[[self.lat, self.lon]].iterrows():
                print(row[0], row[1], 42.0, file=f)

        driver.plot_geopoints(path)


helper = PandasPlotter
