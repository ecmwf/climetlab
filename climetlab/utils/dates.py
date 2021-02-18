# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime

# from collections import defaultdict
from climetlab.helpers import helper
import numpy as np

# datetime.fromisoformat() only available from Python3.7
# from backports.datetime_fromisoformat import MonkeyPatch
from dateutil.parser import isoparse, parse

# MonkeyPatch.patch_fromisoformat()


def parse_date(dt_str):
    try:
        return datetime.datetime.fromisoformat(dt_str)
    except Exception:
        pass

    try:
        return isoparse(dt_str)
    except ValueError:
        return parse(dt_str)


def to_datetime(dt):
    if isinstance(dt, datetime.datetime):
        return dt

    if isinstance(dt, datetime.date):
        return datetime.datetime(dt.year, dt.month, dt.day)

    if isinstance(dt, np.datetime64):
        return to_datetime(dt.astype(datetime.datetime))

    if isinstance(dt, str):
        return parse_date(dt)

    if getattr(dt, "to_datetime", None) is None:
        dt = helper(dt)

    return to_datetime(dt.to_datetime())


def to_datetimes_list(datetimes):
    if isinstance(datetimes, (datetime.datetime, np.datetime64, str)):
        return to_datetimes_list([datetimes])

    if isinstance(datetimes, (list, tuple)):
        return [to_datetime(x) for x in datetimes]

    if getattr(datetimes, "to_datetime_list", None) is None:
        datetimes = helper(datetimes)

    return to_datetimes_list(datetimes.to_datetime_list())


def to_dates_and_times(datetimes_list):
    assert False, datetimes_list
    # result = []
    # datetimes = defaultdict(set)

    # for dt in to_datetimes_list(datetimes_list):
    #     datetimes[dt.date())].add(dt.time())

    # timedates = defaultdict(set)
    # for date, times in sorted(datetimes.items()):
    #     times = tuple(sorted(times))
    #     timedates[times].add(date)

    # for times, dates in timedates.items():
    #     result.append((tuple(sorted(dates)), times))

    # return sorted(result)


def to_date_list(obj):
    return sorted(set(to_datetimes_list(obj)))
