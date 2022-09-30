# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging

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

    def mutate(self):
        return self.index
