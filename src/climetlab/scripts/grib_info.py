# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import logging
import re
import sys

from .tools import parse_args

LOG = logging.getLogger(__name__)


class GribInfoCmd:
    @parse_args(
        param=dict(type=str, help="Comma separated list of parameters."),
        json=dict(action="store_true", help="Long json output format."),
        stdin=dict(action="store_true", help="Using stdin as input (for bash piping)."),
    )
    def do_grib_info(self, args):
        """
        Display information about grib parameters.
        """
        from climetlab.vocabularies.grib import param_id_to_dict

        def iter_params():
            if args.param:
                for p in args.param.split(","):
                    yield p
            if args.stdin:
                for line in sys.stdin:
                    line = line.strip("\n").strip("\r\n")
                    for lst in re.split(r"\s+", line):
                        for lst_ in re.split(",", lst):
                            yield lst_

        for param in iter_params():
            entry = None

            if param.isdigit():
                p = int(param)
                entry = param_id_to_dict(p)

            if entry is None:
                raise NotImplementedError(f"No info found for {param}")

            if args.json:
                s = json.dumps(entry, sort_keys=True, indent=4)
                print(s)
            else:
                print(entry["param_shortName"])
