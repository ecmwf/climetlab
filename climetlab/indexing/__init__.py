# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import warnings


class GlobalIndex:
    def __init__(self, index_location, baseurl) -> None:
        warnings.warn(
            "GlobalIndex is obsolete. Please update your code and use the 'directory' source"
        )
        raise NotImplementedError(
            "GlobalIndex is obsolete. Please update your code and use the 'directory' source"
        )
        """The GloblaIndex has one index managing multiple urls/files.
        This unique index is found at "index_location"
        The path of each file is written in the index as a relative path.
        It is relative to a base url: "baseurl".
        """


class PerUrlIndex:
    def __init__(
        self,
        pattern,
    ) -> None:

        # warnings.warn( "PerUrlIndex is obsolete.")

        self.pattern = pattern
