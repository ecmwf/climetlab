# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
from importlib import import_module

LOG = logging.getLogger(__name__)

SERIALISATION = {}


def register_serialisation(cls, serialise, create):
    fullname = (cls.__module__, cls.__qualname__)
    SERIALISATION[fullname] = (serialise, create)


def serialise_state(obj):
    fullname = (obj.__class__.__module__, obj.__class__.__qualname__)
    LOG.info("serialise %s", fullname)
    return (fullname, SERIALISATION[fullname][0](obj))


def deserialise_state(state):
    fullname, args = state
    LOG.info("deserialise %s %s", fullname, args)
    # warnings.warn('deserialise %s %s', fullname, args)
    # TODO: if KeyError, maybe the function is not imported
    module, _ = fullname
    import_module(module)

    create = SERIALISATION[fullname][1]
    return create(args)
