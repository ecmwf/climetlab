# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from climetlab.helpers import helper as get_helper


class NumpyArrayHelper:
    def __init__(self, data):
        self.data = data

    def plot_map(self, driver):
        # field = driver.option("field")
        # grid = driver.option("grid")
        metadata = get_helper(driver.option("metadata"))
        metadata = metadata.field_metadata()

        driver.bounding_box(
            north=metadata.get("north", 90),
            south=metadata.get("south", -90),
            west=metadata.get("west", 0),
            east=metadata.get("east", 360),
        )

        driver.plot_numpy(
            self.data.reshape(metadata.get("shape", self.data.shape)),
            metadata=metadata,
        )


helper = NumpyArrayHelper
