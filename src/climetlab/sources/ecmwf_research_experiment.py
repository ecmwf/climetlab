# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from .ecmwf_data_server_base import DatasetRetrieverBase


class ExperimentRetriever(DatasetRetrieverBase):
    def __init__(self, experiment, *args, **kwargs):
        extra = {"class": "rd", "expver": experiment}
        super().__init__("research", *args, **kwargs, **extra)


source = ExperimentRetriever
