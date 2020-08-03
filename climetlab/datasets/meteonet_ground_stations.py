# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import pandas as pd

from . import Dataset
from climetlab import load_source


class MeteonetGroundStations(Dataset):
    """
    See https://github.com/meteofrance/meteonet
    """

    def __init__(self, domain='NW', date='20160101'):

        URL = "https://github.com/meteofrance/meteonet/raw/master/data_samples/ground_stations"
        url = "{url}/{domain}_{date}.csv".format(url=URL, domain=domain, date=date)
        self._pandas = pd.read_csv(load_source("url", url).path, parse_dates=[4], infer_datetime_format=True)

    def to_pandas(self):
        return self._pandas


dataset = MeteonetGroundStations
