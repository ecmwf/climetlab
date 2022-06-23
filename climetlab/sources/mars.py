# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os
import subprocess

import ecmwfapi

from climetlab.core.settings import SETTINGS
from climetlab.core.temporary import temp_file

from .ecmwf_api import ECMWFApi, MARSAPIKeyPrompt

LOG = logging.getLogger(__name__)


class StandaloneMarsClient:
    EXE = "/usr/local/bin/mars"

    def execute(self, request, target):
        req = ["retrieve,"]

        for k, v in request.items():
            if isinstance(v, (list, tuple)):
                v = "/".join([str(x) for x in v])
            req += [f"{k}={v},"]

        req += [f'target="{target}"']
        req_str = "\n".join(req)
        with temp_file() as filename:
            with open(filename, "w") as f:
                f.write(req_str + "\n")
            LOG.debug(f"Sending Mars request: '{req_str}'")

            subprocess.run([self.EXE, filename], check=True)


class MARSRetriever(ECMWFApi):
    def service(self):
        if SETTINGS.get("use-standalone-mars-client-when-available"):
            if os.path.exists(StandaloneMarsClient.EXE):
                return StandaloneMarsClient()

        prompt = MARSAPIKeyPrompt()
        prompt.check()

        try:
            return ecmwfapi.ECMWFService("mars")
        except Exception as e:
            if ".ecmwfapirc" in str(e):
                prompt.ask_user_and_save()
                return ecmwfapi.ECMWFService("mars")

            raise


source = MARSRetriever
