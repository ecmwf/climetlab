# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

try:
    import codc as odc
except Exception as e:
    import pyodc as odc
    print("Using pure Python odc decoder which is slow:", e)


class ODBReader:

    def __init__(self, path):
        self.path = path

    def to_pandas(self):
        return odc.read_odb_oneshot(self.path)
