# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os
from collections import defaultdict

from climetlab.utils import download_and_cache


class Part:
    def __init__(self, path, offset, length):
        assert path is not None
        self.path = path
        self.offset = offset
        self.length = length

    def __eq__(self, other):
        return (
            self.path == other.path
            and self.offset == other.offset
            and self.length == other.length
        )

    @classmethod
    def resolve(cls, parts, directory=None):
        paths = defaultdict(list)
        for i, part in enumerate(parts):
            paths[part.path].append(part)

        for path, bits in paths.items():
            if (
                path.startswith("http://")
                or path.startswith("https://")
                or path.startswith("ftp://")
            ):
                newpath = download_and_cache(
                    path, parts=[(p.offset, p.length) for p in bits]
                )
                newoffset = 0
                for p in bits:
                    p.path = newpath
                    p.offset = newoffset
                    newoffset += p.length

            elif directory and not os.path.isabs(path):
                for p in bits:
                    p.path = os.path.join(directory, path)

        return parts

    def __repr__(self):
        return f"Part[{self.path},{self.offset},{self.length}]"
