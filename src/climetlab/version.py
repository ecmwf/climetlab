# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os


def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "version")
    with open(version_file, "r") as f:
        version = f.readlines()
        version = version[0]
        version = version.strip()
    return version


__version__ = get_version()
