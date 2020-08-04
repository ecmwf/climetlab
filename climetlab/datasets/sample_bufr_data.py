# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from . import Dataset
from climetlab import load_source


class SampleBUFRData(Dataset):
    def __init__(
        self, url="http://download.ecmwf.int/test-data/metview/gallery/temp.bufr"
    ):
        self.source = load_source("url", url)


dataset = SampleBUFRData
