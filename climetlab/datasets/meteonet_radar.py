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


class MeteonetRadar(Dataset):
  """
  See https://github.com/meteofrance/meteonet
  """

  def __init__(self, domain='NW', parameter='rainfall', year=2016, month=8, part=3):

    URL = "https://github.com/meteofrance/meteonet/raw/master/data_samples/radar"

    url = "{url}/radar_coords_{domain}.npz".format(url=URL, domain=domain)
    coords = np.load(load_source("url", url).path, allow_pickle=True)

    resolution = 0  # 0.01

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
    print(data.shape)

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

    ds["lon"].attrs["standard_name"] = "longitude"
    ds["lat"].attrs["standard_name"] = "latitude"
    ds["time"].attrs["standard_name"] = "time"

    ds.to_netcdf(path + ".nc")
    self.source = load_source("file", path + ".nc")


dataset = MeteonetRadar
