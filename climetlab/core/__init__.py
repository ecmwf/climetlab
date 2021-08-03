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
        self._not_implemented()

    def to_xarray(self, **kwargs):
        self._not_implemented()

    def to_pandas(self, **kwargs):
        self._not_implemented()

    def to_tfdataset(self, **kwargs):
        self._not_implemented()

    def to_metview(self, **kwargs):
        self._not_implemented()

    # Change class
    def mutate(self):
        return self

    # Used when plotting
    def plot_map(self, driver):
        self._not_implemented()

    def field_metadata(self):
        self._not_implemented()

    # I/O
    def save(self, path):
        self._not_implemented()

    def write(self, f):
        self._not_implemented()

    # Used by normalisers
    def to_datetime(self):
        self._not_implemented()

    def to_datetime_list(self):
        self._not_implemented()

    def to_bounding_box(self):
        self._not_implemented()

    #
    def _not_implemented(self):
        import inspect

        func = inspect.stack()[1][3]
        module = self.__class__.__module__
        name = self.__class__.__name__

        extra = ""
        if hasattr(self, "path"):
            extra = self.path
        raise NotImplementedError(f"{module}.{name}.{func}({extra})")
