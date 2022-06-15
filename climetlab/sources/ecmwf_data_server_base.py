# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import ecmwfapi

from .ecmwf_api import ECMWFApi


class Wrapper(ecmwfapi.ECMWFDataServer):
    def __init__(self, dataset):
        super().__init__()
        self.dataset = dataset

    def execute(self, request, target):
        request = dict(**request)
        request["dataset"] = self.dataset
        request["target"] = target
        print(request)
        return self.retrieve(request)


class DatasetRetrieverBase(ECMWFApi):
    def __init__(self, dataset, *args, **kwargs):
        self.ecmwf_dataset = dataset
        super().__init__(*args, **kwargs)

    def service(self):
        return Wrapper(self.ecmwf_dataset)
