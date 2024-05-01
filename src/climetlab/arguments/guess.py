# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

LOG = logging.getLogger(__name__)


def guess_type_list(lst):
    assert isinstance(lst, (tuple, list))

    for typ in [int, float, str]:
        if all([isinstance(x, typ) for x in lst]):
            return typ

    return None
