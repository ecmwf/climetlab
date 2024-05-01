# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from .era5_single_levels import Era5SingleLevels


class Era5Precipitations(Era5SingleLevels):
    def __init__(self, *args, **kwargs):
        super().__init__("tp", *args, **kwargs)


dataset = Era5Precipitations
