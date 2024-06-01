# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from climetlab.wrappers import Wrapper


class NoneWrapper(Wrapper):
    def __init__(self, data):
        pass

    def plot_map(self, backend):
        pass

    def field_metadata(self):
        return {}


def wrapper(data, *args, **kwargs):
    if data is None:
        return NoneWrapper(data)
    return None
