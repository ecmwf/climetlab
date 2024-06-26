# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

LOG = logging.getLogger(__name__)


def reader(source, path, magic=None, deeper_check=False):
    if magic is None or magic[:4] == b"GRIB":
        from .reader import GRIBReader

        return GRIBReader(source, path)

    if deeper_check:
        with open(path, "rb") as f:
            magic = f.read(1024)
            if b"GRIB" in magic:
                from .reader import GRIBReader

                return GRIBReader(source, path)
