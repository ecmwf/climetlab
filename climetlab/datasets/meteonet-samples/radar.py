# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import numpy as np
import xarray as xr

from climetlab.utils import download_and_cache

from . import Meteonet

"""
rainfall_diff_quality-code
rainfall_mean_quality-code
reflectivity_new
reflectivity_old
"""


class MeteonetRadar(Meteonet):
    """
    See https://github.com/meteofrance/meteonet
    """

    def __init__(self, domain="NW", variable="rainfall", year=2016, month=8, part=3):

        url = "{url}/radar/radar_coords_{domain}.npz".format(
            url=self.URL, domain=domain
        )

        coords = np.load(download_and_cache(url), allow_pickle=True)

        resolution = 0.01

        lats = coords["lats"] - resolution / 2
        lons = coords["lons"] + resolution / 2

        url = "{url}/radar/{variable}_{domain}_{year}_{month:02d}.{part}.npz".format(
            url=self.URL,
            domain=domain,
            variable=variable,
            year=year,
            month=month,
            part=part,
        )

        path = download_and_cache(url)
        content = np.load(path, allow_pickle=True)
        data = content["data"]
        times = content["dates"]
        # missing = content['miss_dates']

        self.variable = variable

        ds = xr.Dataset(
            {
                variable: (["time", "y", "x"], data),
                "x": (["x"], range(0, data.shape[2])),
                "y": (["y"], range(0, data.shape[1])),
            },
            coords={
                "lon": (["y", "x"], lons),
                "lat": (["y", "x"], lats),
                "time": times,
            },
        )

        self.north = np.amax(lats)
        self.south = np.amin(lats)
        self.east = np.amax(lons)
        self.west = np.amin(lons)

        ds["lon"].attrs["standard_name"] = "longitude"
        ds["lat"].attrs["standard_name"] = "latitude"
        ds["time"].attrs["standard_name"] = "time"
        ds["x"].attrs["axis"] = "X"
        ds["y"].attrs["axis"] = "Y"

        self._xarray = ds

    def to_xarray(self):
        return self._xarray

    def plot_map(self, driver):
        driver.bounding_box(self.north, self.west, self.south, self.east)

        dimensions = {"time": 0}

        driver.plot_xarray(self._xarray, self.variable, dimensions)
        driver.style("meteonet-samples-radar-{}".format(self.variable))


dataset = MeteonetRadar
