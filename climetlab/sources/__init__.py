# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from importlib import import_module


def load(name, *args, **kwargs):
    source = import_module('.%s' % (name.replace('-', '_'),), package=__name__)
    return source.source(*args, **kwargs)


class DataSource:
    pass
