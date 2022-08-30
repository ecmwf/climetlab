# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import copy
import logging

LOG = logging.getLogger(__name__)


def deep_update(old, new):
    # deep update, merging dictionaries
    assert isinstance(new, dict), f"Expecting a dict, but received: {new}"
    for k, v in new.items():
        v = new[k]
        if k in old and isinstance(old[k], dict):
            deep_update(old[k], v)
        else:
            old[k] = v
    return old


class Kwargs(dict):
    def __init__(
        self,
        user,
        default=None,
        forced=None,
        logging_owner="",
        logging_main_key="",
    ):
        if default is None:
            default = {}

        if forced is None:
            forced = {}

        kwargs = copy.deepcopy(default)

        for k, v in user.items():
            if k in forced and v != forced[k]:
                LOG.warning(
                    (
                        f"In {logging_owner} {logging_main_key},"
                        f"ignoring attempt to override {k}={forced[k]} with {k}={v}."
                    )
                )
                continue

            if k in default and v != default[k]:
                LOG.warning(
                    (
                        f"In {logging_owner} {logging_main_key}, overriding the default value "
                        f"({k}={default[k]}) with {k}={v} is not recommended."
                    )
                )

            kwargs[k] = v

        kwargs.update(forced)

        super().__init__(kwargs)


# TODO: add test (and fix bugs)
def merge_dicts(*dicts):
    result = {}
    for v in dicts:
        result = deep_update(result, v)
    return result
