# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

# import os
# import tempfile
import hashlib
from .settings import SETTINGS


def update(m, x):
    if isinstance(x, (list, tuple)):
        for y in x:
            update(m, y)
        return

    if isinstance(x, dict):
        for k, v in sorted(x.items()):
            update(m, k)
            update(m, v)
        return

    m.update(str(x).encode("utf-8"))


def temp_file(*args, extension=".cache"):
    m = hashlib.sha256()
    update(m, args)
    # fd, path = tempfile.mkstemp()
    # os.close(fd)
    return "%s/climetlab-%s%s" % (SETTINGS["cache_directory"], m.hexdigest(), extension)
