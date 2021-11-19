# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import datetime
import re

import numpy as np

# datetime.fromisoformat() only available from Python3.7
# from backports.datetime_fromisoformat import MonkeyPatch
from dateutil.parser import isoparse, parse

from climetlab.utils.domains import domain_to_area

# from collections import defaultdict
from climetlab.wrappers import Wrapper, get_wrapper

# MonkeyPatch.patch_fromisoformat()


VALID_DATE = re.compile(r"\d\d\d\d-?\d\d-?\d\d([T\s]\d\d:\d\d(:\d\d)?)?Z?")


def parse_date(dt):

    if not isinstance(dt, str):
        return to_datetime(dt)

    if not VALID_DATE.match(dt):
        raise ValueError(f"Invalid datetime '{dt}'")

    try:
        return datetime.datetime.fromisoformat(dt)
    except Exception:
        pass

    try:
        return isoparse(dt)
    except ValueError:
        pass

    return parse(dt)


class StrWrapper(Wrapper):
    def __init__(self, data):
        self.data = data

    def to_bounding_box(self):
        return domain_to_area(self.data)


def wrapper(data, *args, **kwargs):
    if isinstance(data, str):
        return StrWrapper(data)
    return None
