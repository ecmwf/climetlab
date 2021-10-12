#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

import pytest

import climetlab as cml

LOG = logging.getLogger(__name__)


@pytest.mark.long_test
@pytest.mark.external_download
def test_load_dataset_meteonet_sample_masks():
    cml.load_dataset("meteonet-samples-masks", domain="SE")
