# (C) Copyright 2020- ECMWF.  #
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
from abc import abstractmethod
from collections import defaultdict

import climetlab
from climetlab.loaders import build_remapping

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

    def to_pytorch_dataset(self, *args, **kwargs):
        self._not_implemented()

    def set_options(self, *args, **kwargs):
        if not hasattr(self, "_options"):
            self._options = {}
        for dic in args:
            self.set_options(**dic)
        if kwargs:
            self._options.update(**kwargs)

    def get_options(self):
        if not hasattr(self, "_options"):
            self._options = {}
        return self._options

    def cube(self, *args, **kwargs):
        from climetlab.indexing.cube import FieldCube

        return FieldCube(self, *args, **kwargs)

    def get_metadata(self, i):
        return self[i].metadata()

    def unique_values(self, *coords, remapping=None, progress_bar=True):
        """
        Given a list of metadata attributes, such as date, param, levels,
        returns the list of unique values for each attributes
        """

        assert len(coords)
        assert all(isinstance(k, str) for k in coords), coords

        remapping = build_remapping(remapping)
        iterable = self

        if progress_bar:
            iterable = climetlab.utils.progress_bar(
                iterable=self,
                desc=f"Finding coords in dataset for {coords}",
            )

        dic = defaultdict(dict)
        for f in iterable:
            metadata = remapping(f.metadata)
            for k in coords:
                v = metadata(k)
                dic[k][v] = True

        dic = {k: tuple(values.keys()) for k, values in dic.items()}

        return dic

    def combinations(self, *coords, progress_bar=True):
        assert all(isinstance(k, str) for k in coords), coords

        iterable = self

        if progress_bar:
            iterable = climetlab.utils.progress_bar(
                iterable=self,
                desc=f"Finding coords in dataset for {coords}",
            )

        for f in iterable:
            yield {k: f.metadata(k) for k in coords}

    def __add__(self, other):
        self._not_implemented()

    def _not_implemented(self):
        import inspect

        func = inspect.stack()[1][3]
        module = self.__class__.__module__
        name = self.__class__.__name__

        extra = ""
        if hasattr(self, "path"):
            extra = f" on {self.path}"
        raise NotImplementedError(f"{module}.{name}.{func}(){extra}")
