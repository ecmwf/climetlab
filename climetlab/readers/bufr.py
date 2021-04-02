# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# See:
# https://github.com/ecmwf/pdbufr
from . import Reader

COLUMNS = ("latitude", "longitude", "data_datetime")


class BUFRReader(Reader):
    def to_pandas(self, columns=COLUMNS, filters=None, **kwargs):
        import pdbufr

        return pdbufr.read_bufr(self.path, columns=columns, filters=filters)
