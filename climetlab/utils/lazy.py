# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

from climetlab import load_source

LOG = logging.getLogger(__name__)


class LazySourceError:
    def __init__(self, owner, error):
        self.owner = owner
        self.error = error


class LazySource:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self._source = None

    def __call__(self, **kwargs):
        assert self._source is None
        self.kwargs.update(kwargs)
        return self.source

    @property
    def source(self):
        if self._source is None:
            try:
                self._source = load_source(
                    self.name,
                    lazily=False,
                    *self.args,
                    **self.kwargs,
                )
            except Exception:
                LOG.exception(
                    "Error loading source %s(%s, %s)",
                    self.name,
                    self.args,
                    self.kwargs,
                )

        return self._source

    def __getitem__(self, name):
        return self.source[name]

    def __iter__(self):
        return iter(self.source)

    def __len__(self):
        return len(self.source)

    def __getattr__(self, name):
        assert name != "source"
        return getattr(self.source, name)
