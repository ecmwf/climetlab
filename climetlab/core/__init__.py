# (C) Copyright 2020 ECMWF.  #
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# This empty __init__.py is there to help find_packages() (in setup.py)
# to include this folder in the tar uploaded at pip

"""
Find me

.. autosummary::
    climetlab.core.Base

"""


class Base:

    # Convertors
    def to_numpy(self, **kwargs):
        raise NotImplementedError()

    def to_xarray(self, **kwargs):
        raise NotImplementedError()

    def to_pandas(self, **kwargs):
        raise NotImplementedError()

    def to_metview(self, **kwargs):
        raise NotImplementedError()

    # Used when plotting
    def plot_map(self, driver):
        raise NotImplementedError()

    def field_metadata(self):
        raise NotImplementedError()

    # Used by normalisers
    def to_datetime(self):
        raise NotImplementedError()

    def to_datetime_list(self):
        raise NotImplementedError()

    def to_bounding_box(self):
        raise NotImplementedError()
