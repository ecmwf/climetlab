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

    @alias_argument("levelist", ["level"])
    @alias_argument("param", ["variable", "parameter"])
    @alias_argument("number", ["realization", "realisation"])
    @alias_argument("class", "klass")
    def __init__(self, index=None, filter=None, merger=None, **kwargs):
        self.filter = filter
        self.merger = merger
        self.index = index.sel(kwargs)

        super().__init__()

    @property
    def availability(self):
        return self.index.availability

    @abstractmethod
    def sel(self, **kwargs):
        return self._not_implemented()

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
