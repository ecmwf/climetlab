# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from climetlab.wrappers import get_wrapper

from . import Reader

LOG = logging.getLogger(__name__)


class FWFReader(Reader):
    def __init__(self, source, path, header=None):
        super().__init__(source, path)
        self.header = header

    def to_pandas(self, **kwargs):
        import pandas

        pandas_read_fwf_kwargs = kwargs.get("pandas_read_fwf_kwargs", {})

        LOG.debug(
            "pandas.read_fwf(%s,header=%s,%s)",
            self.path,
            self.header,
            pandas_read_fwf_kwargs,
        )
        return pandas.read_fwf(
            self.path,
            header=self.header,
            **pandas_read_fwf_kwargs,
        )

    def plot_graph(self, backend):
        get_wrapper(self.to_pandas()).plot_graph(backend)

    def plot_map(self, backend):
        get_wrapper(self.to_pandas()).plot_map(backend)


def reader(source, path, magic=None, deeper_check=False):

    if magic is None:  # Bypass check and force
        return FWFReader(source, path)

    # For now, only created if magic is None


aliases = ["fix_width_format"]
