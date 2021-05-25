# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from climetlab import load_source

from . import Meteonet


class MeteonetWeatherModels(Meteonet):
    """
    See https://github.com/meteofrance/meteonet
    """

    def __init__(
        self, model="arome", variable="2m", domain="NW", date="20180501", time="0000"
    ):

        url = "{url}/weather_models/{model}_{variable}_{domain}_{date}{time}00.grib".format(
            url=self.URL,
            variable=variable,
            model=model,
            domain=domain,
            date=date,
            time=time,
        )
        self.source = load_source("url", url)


dataset = MeteonetWeatherModels
