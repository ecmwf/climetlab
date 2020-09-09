# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging
import os
from collections import defaultdict

import yaml

from climetlab.core.data import get_data_entry

from .actions import lookup

LOG = logging.getLogger(__name__)


MAGICS_KEYS = None


def _magics_keys():
    global MAGICS_KEYS

    if MAGICS_KEYS is None:
        MAGICS_KEYS = defaultdict(set)
        with open(os.path.join(os.path.dirname(__file__), "magics.yaml")) as f:
            magics = yaml.load(f, Loader=yaml.SafeLoader)
            for name, params in magics.items():
                for param in params:
                    MAGICS_KEYS[param].add(name)
    return MAGICS_KEYS


def _find_action(value, action):

    magics_keys = _magics_keys()

    # Guess the best action from the keys
    scores = defaultdict(int)
    special = 0
    for param in value.keys():

        if not param[0].isalpha():
            special += 1
            param = param[1:]

        acts = magics_keys.get(param, [])
        if len(acts) == 1:
            # Only consider unambiguous parameters
            scores[list(acts)[0]] += 1

    best = sorted((v, k) for k, v in scores.items())

    if len(best) == 0:
        LOG.warning("Cannot establish Magics action from [%r]", list(value.keys()))

    if len(best) >= 2 and best[0][0] == best[1][0]:
        LOG.warning(
            "Cannot establish Magics action from [%r], it could be %s or %s",
            list(value.keys()),
            best[0][1],
            best[1][1],
        )

    if len(best) > 0:
        action = lookup(best[0][1])

    return action, special


def _apply_dict(*, value, collection=None, action=None, default=True, target=None):

    if "set" in value or "clear" in value:
        newvalue = {}
        for k, v in value.get("set", {}).items():
            newvalue["+{}".format(k)] = v

        for k in value.get("clear", []):
            newvalue["-{}".format(k)] = None

        return apply(
            value=newvalue,
            collection=collection,
            action=action,
            default=default,
            target=target,
        )

    if "+" in value or "-" in value:
        newvalue = {}
        for k, v in value.get("+", {}).items():
            newvalue["+{}".format(k)] = v

        for k in value.get("-", []):
            newvalue["-{}".format(k)] = None

        return apply(
            value=newvalue,
            collection=collection,
            action=action,
            default=default,
            target=target,
        )

    action, special = _find_action(value, action)
    if special:
        if special != len(value):
            raise ValueError(
                "Cannot set some attributes and override others %r" % list(value.keys())
            )

        result = target.update(action, value)
        if result is not None:
            return result

        raise ValueError(
            "Cannot override attributes %r (no matching style)" % list(value.keys())
        )

    return action(**value)


def _apply_true(*, value, collection=None, action=None, default=True, target=None):
    assert default is not True
    return apply(
        value=default,
        collection=collection,
        action=action,
        default=None,
        target=target,
    )


def _apply_string(*, value, collection=None, action=None, default=True, target=None):

    # TODO: Consider `value` being a URL (yaml or json)

    data = get_data_entry(collection, value).data

    magics = data["magics"]
    actions = list(magics.keys())
    assert len(actions) == 1, actions

    name = actions[0]
    action = lookup(name)
    kwargs = magics[name]
    return action(**kwargs)


def apply(*, value, collection=None, action=None, default=True, target=None):

    if value in (None, False):
        return None

    if value is True:
        return _apply_true(
            value=value,
            collection=collection,
            action=action,
            default=default,
            target=target,
        )

    if isinstance(value, dict):
        return _apply_dict(
            value=value,
            collection=collection,
            action=action,
            default=default,
            target=target,
        )

    if isinstance(value, str):
        return _apply_string(
            value=value,
            collection=collection,
            action=action,
            default=default,
            target=target,
        )

    raise ValueError("Unsupported type %s, %s (%s)" % (type(value), value, collection))
