# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging
from abc import abstractmethod

from climetlab.core.settings import SETTINGS
from climetlab.decorators import alias_argument
from climetlab.sources import Source

LOG = logging.getLogger(__name__)


class IndexedSource(Source):

    _reader_ = None

    def __init__(self, index, order_by=None, filter=None, merger=None, **kwargs):
        LOG.debug(f"New IndexedSource order={order_by} kwargs={kwargs}")
        if order_by is None:
            order_by = {}

        order_by = self.alias_arguments(**order_by)
        kwargs = self.alias_arguments(**kwargs)

        self.filter = filter
        self.merger = merger
        self.index = index

        self.index = self.index.sel(kwargs)
        self.index = self.index.order_by(order_by)

        super().__init__()

    @alias_argument("levelist", ["level"])
    @alias_argument("param", ["variable", "parameter"])
    @alias_argument("number", ["realization", "realisation"])
    @alias_argument("class", "klass")
    def alias_arguments(self, **kwargs):
        return kwargs

    @property
    def availability(self):
        return self.index.availability

    def sel(self, **kwargs):
        kwargs = self.alias_arguments(**kwargs)
        return self.__class__(self, _index=self.index.sel(**kwargs))

    def order_by(self, arg=None, **kwargs):
        kwargs = self.alias_arguments(**kwargs)
        order = dict()
        if arg:
            arg = self.alias_arguments(**arg)
            order.update(arg)
        order.update(kwargs)
        return self.__class__(self, _index=self.index.order_by(order))

    def __getitem__(self, n):
        return self.index[n]

    def __len__(self):
        return len(self.index)

    def __repr__(self):
        cache_dir = SETTINGS.get("cache-directory")

        def to_str(attr):
            if not hasattr(self, attr):
                return None
            out = getattr(self, attr)
            if isinstance(out, str):
                out = out.replace(cache_dir, "CACHE:")
            return out

        args = [f"{x}={to_str(x)}" for x in ("path", "abspath")]
        args = [x for x in args if x is not None]
        args = ",".join(args)
        return f"{self.__class__.__name__}({args})"

    def to_tfdataset(self, *args, **kwargs):
        return self.index.to_tfdataset(*args, **kwargs)

    def to_pytorch(self, *args, **kwargs):
        return self.index.to_pytorch(*args, **kwargs)

    def to_numpy(self, *args, **kwargs):
        return self.index.to_numpy(*args, **kwargs)

    def to_xarray(self, *args, **kwargs):
        return self.index.to_xarray(*args, **kwargs)
