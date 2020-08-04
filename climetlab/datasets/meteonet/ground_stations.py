# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import pandas as pd
import os

from . import Meteonet
from climetlab.utils import download_and_cache


class MeteonetGroundStations(Meteonet):
    """
    See https://github.com/meteofrance/meteonet
    """

    def __init__(self, domain="NW", date="20160101"):

        url = "{url}/ground_stations/{domain}_{date}.csv".format(
            url=self.URL, domain=domain, date=date
        )

        self.path = download_and_cache(url)
        self._pandas = pd.read_csv(
            self.path, parse_dates=[4], infer_datetime_format=True
        )

    def to_pandas(self):
        return self._pandas

    def plot_map(self, driver):

        north, east = self._pandas[["lat", "lon"]].max()
        south, west = self._pandas[["lat", "lon"]].min()

        lats = self._pandas["lat"].to_numpy()
        lons = self._pandas["lon"].to_numpy()
        vals = self._pandas["t"].to_numpy()

        driver.bounding_box(north, west, south, east)

        try:
            os.unlink(self.path + ".geo")
        except Exception:
            pass

        with open(self.path + ".geo", "w") as f:
            print("#GEO", file=f)
            print("#FORMAT XYV", file=f)
            print("min: {}".format(min(vals)), file=f)
            print("max: {}".format(max(vals)), file=f)
            print("x/long  y/lat  value", file=f)
            print("#DATA", file=f)
            for lat, lon, v in zip(lats, lons, vals):
                print(lon, lat, v, file=f)

        driver.plot_geopoints(self.path + ".geo")
        # driver.plot_values(latitudes=lats,
        #                    longitudes=lons,
        #                    values=vals)

        # driver.contouring({})
        # driver.contouring(dict(contour_grid_value_plot=True,
        #                        contour=False,
        #                        contour_grid_value_plot_type='marker'))


dataset = MeteonetGroundStations
