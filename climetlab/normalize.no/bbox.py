# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.utils.bbox import BoundingBox, to_bounding_box

CONVERT = {
    list: lambda x: x.as_list(),
    tuple: lambda x: x.as_tuple(),
    dict: lambda x: x.as_dict(),
    BoundingBox: lambda x: x,
}


class BoundingBoxNormaliser:
    def __init__(self, format=BoundingBox):
        self.format = format

    def normalise(self, bbox):
        bbox = to_bounding_box(bbox)
        return CONVERT[self.format](bbox)
