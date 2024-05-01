# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import bz2

from . import Reader
from . import reader as find_reader


class BZReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

        def uncompress(target, _):
            with open(target, "wb") as g:
                with bz2.open(path, "rb") as f:
                    while True:
                        chunk = f.read(1024 * 1204)
                        if not chunk:
                            break
                        g.write(chunk)

        self.unzipped = self.cache_file(
            uncompress,
            dict(path=path),
        )

    def mutate(self):
        print("mutare", self.source, self.unzipped)
        return find_reader(self.source, self.unzipped)


def reader(source, path, magic=None, deeper_check=False):
    if magic is None:  # Bypass check and force
        return BZReader(source, path)

    if magic[:3] == b"BZh":
        return BZReader(source, path)
