# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import datetime

from climetlab.wrappers import Wrapper, get_wrapper


class NumpyArrayWrapper(Wrapper):
    def __init__(self, data, *args, **kwargs):
        self.data = data

    def plot_map(self, backend):

        wrapper = get_wrapper(backend.option("metadata"))

        if hasattr(wrapper, "plot_numpy"):
            return wrapper.plot_numpy(backend, self.data)

        metadata = wrapper.field_metadata()

        backend.bounding_box(
            north=metadata["north"],
            south=metadata["south"],
            west=metadata["west"],
            east=metadata["east"],
        )

        backend.plot_numpy(
            self.data.reshape(metadata.get("shape", self.data.shape)),
            metadata=metadata,
        )

    def to_datetime_list(self):
        return [datetime.datetime.fromtimestamp(x * 1e-9) for x in self.data.tolist()]


def wrapper(data, *args, **kwargs):
    import numpy as np

    if isinstance(data, np.ndarray):
        return NumpyArrayWrapper(data, *args, **kwargs)
    return None
