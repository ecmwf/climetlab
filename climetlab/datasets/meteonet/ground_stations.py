# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import pandas as pd

from climetlab.utils import download_and_cache

from . import Meteonet


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

        driver.bounding_box(north, west, south, east)
        driver.plot_pandas(self._pandas, "lat", "lon", "t")


dataset = MeteonetGroundStations
