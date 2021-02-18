# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.core.bbox import to_bounding_box


class BoundingBoxNormaliser:
    def __init__(self, format=None):
        self.format = format
        assert self.format == "list", format

    def normalise(self, bbox):
        bbox = to_bounding_box(bbox)
        return bbox.as_list()
