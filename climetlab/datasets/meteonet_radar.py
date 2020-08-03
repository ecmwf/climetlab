# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import numpy as np
import xarray as xr

from . import Dataset
from climetlab import load_source


"""
rainfall_diff_quality-code
rainfall_mean_quality-code
reflectivity_new
reflectivity_old
"""


class MeteonetRadar(Dataset):
    """
    See https://github.com/meteofrance/meteonet
    """

    def __init__(self, domain='NW', parameter='rainfall', year=2016, month=8, part=3):

        URL = "https://github.com/meteofrance/meteonet/raw/master/data_samples/radar"

        url = "{url}/radar_coords_{domain}.npz".format(url=URL, domain=domain)
        coords = np.load(load_source("url", url).path, allow_pickle=True)

        resolution = 0.01

        lats = coords['lats'] - resolution / 2
        lons = coords['lons'] + resolution / 2

        url = "{url}/{parameter}_{domain}_{year}_{month:02d}.{part}.npz".format(
            url=URL,
            domain=domain,
            parameter=parameter,
            year=year,
            month=month,
            part=part,
        )

        path = load_source("url", url).path
        content = np.load(path, allow_pickle=True)
        data = content['data']
        times = content['dates']
        # missing = content['miss_dates']
        # print(len(dates))
        # print(data.shape)

        self.variable = parameter

        ds = xr.Dataset(
            {
                parameter: (["time", "y", "x", ], data),
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

        self.path = path + ".nc"

        ds.to_netcdf(self.path)
        self.source = load_source("file", path + ".nc")

    def to_array(self):
        return self._xarray

    def plot_map(self, driver):
        driver.bounding_box(self.north, self.west,
                            self.south, self.east)

        dimensions = ["time:0"]

        driver.plot_netcdf(dict(netcdf_filename=self.path,
                                netcdf_value_variable=self.variable,
                                netcdf_dimension_setting=dimensions,
                                netcdf_dimension_setting_method='index'))

        driver.contouring(self.contouring)

    @property
    def contouring(self):
        return dict(
            contour_shade_colour_method="list",
            # contour_shade_method = "area_fill",
            contour_shade_technique='grid_shading',
            contour_shade="on",
            contour_hilo="off",
            contour="off",
            contour_highlight="off",
            contour_label="off",
            contour_shade_colour_list=['#C0C0C0',
                                       'rgba(0,0,0,0)', '#483D8B', '#0000cd', '#1E90FF',
                                       '#87ceeb', 'olive', '#3cb371', 'cyan', '#00FF00', 'yellow',
                                       'khaki', 'burlywood', 'orange', 'brown', 'pink', 'red', 'plum'],
            contour_level_list=[float(x) for x in [-1, 0, 2, 4, 6, 8, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 75]],
            #                contour_shade_min_level=0.5
        )


dataset = MeteonetRadar
