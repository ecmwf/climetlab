# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging

from climetlab.core.settings import SETTINGS
from climetlab.sources import Source

LOG = logging.getLogger(__name__)


class IndexedSource(Source):

    _reader_ = None

    def __init__(self, index, order_by=None, filter=None, merger=None, **kwargs):
        LOG.debug(f"New IndexedSource order={order_by} kwargs={kwargs}")

        def _build_order_by_from_selection(selection):
            if not selection:
                return None
            order_by = {}
            for k, v in selection.items():
                if v is None:
                    order_by[k] = v
                elif isinstance(v, (list, tuple)):
                    order_by[k] = v
                else:
                    # There is only one element for this key in the request.
                    # No need to sort along this dimension
                    pass
                    # TODO: remove this comment:
                    # We could still keep this key to ensure consistency: when coming from a request,
                    # the values of order_by would be either None or a list with the following.
                    #   either:
                    #      order_by[k] = [v]
                    #   or:
                    #      order_by[k] = None
            return order_by

        if order_by is None:
            order_by = _build_order_by_from_selection(kwargs)

        self.filter = filter
        self.merger = merger
        self.index = index

        if kwargs:
            self.index = self.index.sel(kwargs)

        if order_by:
            self.index = self.index.order_by(order_by)

        super().__init__()

    @property
    def availability(self):
        return self.index.availability

    def sel(self, *args, **kwargs):
        index = self.index.sel(*args, **kwargs)
        return self.__class__(self, _index=index)

    def order_by(self, *args, **kwargs):
        index = self.index.order_by(*args, **kwargs)
        return self.__class__(self, _index=index)

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
