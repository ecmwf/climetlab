# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from .. import Reader
from .fieldset import NetCDFFieldSetFromFile


class NetCDFReader(Reader, NetCDFFieldSetFromFile):
    def __init__(self, source, path):
        Reader.__init__(self, source, path)
        NetCDFFieldSetFromFile.__init__(self, path)


def reader(source, path, magic=None, deeper_check=False):
    if magic is None or magic[:4] in (b"\x89HDF", b"CDF\x01", b"CDF\x02"):
        return NetCDFReader(source, path)
