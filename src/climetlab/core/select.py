# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import logging

LOG = logging.getLogger(__name__)


def normalize_selection(*args, **kwargs):
    from climetlab.arguments.transformers import ALL

    _kwargs = {}
    for a in args:
        if a is None:
            continue
        if isinstance(a, dict):
            _kwargs.update(a)
            continue
        raise ValueError(f"Cannot make a selection with {a}")

    _kwargs.update(kwargs)

    for k, v in _kwargs.items():
        assert (
            v is None
            or v is ALL
            or callable(v)
            or isinstance(v, (list, tuple, set))
            or isinstance(v, (str, int, float, datetime.datetime))
        ), f"Unsupported type: {type(v)} for key {k}"
    return _kwargs
