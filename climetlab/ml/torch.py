# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

import torch

LOG = logging.getLogger(__name__)


def _find_device():
    if torch.cuda.is_available():
        LOG.debug("Found Cuda device")
        return "cuda"

    import platform

    if platform.system() == "Darwin" and platform.processor() == "arm":  # macos M1
        LOG.debug("Found M1 device on Macos")
        return "mps"

    LOG.debug("Found no GPU, using CPU")
    return "cpu"


device = _find_device()
