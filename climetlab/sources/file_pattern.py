# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.utils.pattern import Pattern

from . import File, MultiSource


class FilePattern(MultiSource):
    def __init__(self, pattern, *args, **kwargs):
        files = Pattern(pattern).substitute(*args, **kwargs)
        if not isinstance(files, list):
            files = [files]

        sources = [File(file) for file in files]
        super().__init__(sources)


source = FilePattern
