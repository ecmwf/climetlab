# (C) Copyright 2020- ECMWF.  #
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
from abc import abstractmethod

LOG = logging.getLogger(__name__)

PRIVATE_ATTRIBUTES = {"observer": lambda: None}


class MetaBase(type):
    def __call__(cls, *args, **kwargs):
        obj = cls.__new__(cls, *args, **kwargs)
        args, kwargs = cls.patch(obj, *args, **kwargs)
        obj.__init__(*args, **kwargs)
        return obj

    def patch(cls, obj, *args, **kwargs):
        private_attributes = {}
        private_attributes.update(PRIVATE_ATTRIBUTES)
        private_attributes.update(kwargs.pop("_PRIVATE_ATTRIBUTES", {}))

        for k, v in private_attributes.items():
            setattr(obj, k, kwargs.pop(k, v))

        return args, kwargs


class Base(metaclass=MetaBase):

    # Convertors
    def to_numpy(self, **kwargs):
        self._not_implemented()

    @abstractmethod
    def to_xarray(self, **kwargs):
        self._not_implemented()

    @abstractmethod
    def to_pandas(self, **kwargs):
        self._not_implemented()

    @abstractmethod
    def to_tfdataset(self, **kwargs):
        self._not_implemented()

    @abstractmethod
    def to_metview(self, **kwargs):
        self._not_implemented()

    # Change class
    def mutate(self):
        return self

    @classmethod
    def merge(cls, *args, **kwargs):
        return None

    # Used when plotting
    @abstractmethod
    def plot_map(self, backend):
        self._not_implemented()

    @abstractmethod
    def plot_graph(self, backend):
        self._not_implemented()

    @abstractmethod
    def field_metadata(self):
        self._not_implemented()

    # I/O
    @abstractmethod
    def save(self, path):
        self._not_implemented()

    @abstractmethod
    def write(self, f):
        self._not_implemented()

    # Used by normalisers
    @abstractmethod
    def to_datetime(self):
        self._not_implemented()

    @abstractmethod
    def to_datetime_list(self):
        self._not_implemented()

    @abstractmethod
    def to_bounding_box(self):
        self._not_implemented()

    # For machine learning
    @abstractmethod
    def statistics(self):
        self._not_implemented()

    @abstractmethod
    def scaled(self, args, kwargs):
        self._not_implemented()

    @abstractmethod
    def sel(self, *args, **kwargs):
        self._not_implemented()

    @abstractmethod
    def order_by(self, *args, **kwargs):
        self._not_implemented()

    #
    def _not_implemented(self):
        import inspect

        func = inspect.stack()[1][3]
        module = self.__class__.__module__
        name = self.__class__.__name__

        extra = ""
        if hasattr(self, "path"):
            extra = f" on {self.path}"
        raise NotImplementedError(f"{module}.{name}.{func}(){extra}")
