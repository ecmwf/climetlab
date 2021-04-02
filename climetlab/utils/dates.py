# (C) Copyright 2020 ECMWF.
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

# from collections import defaultdict
from climetlab.helpers import helper

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


def to_datetime(dt):
    if isinstance(dt, datetime.datetime):
        return dt

    if isinstance(dt, datetime.date):
        return datetime.datetime(dt.year, dt.month, dt.day)

    if isinstance(dt, np.datetime64):
        # Looks like numpy dates conversion vary
        dt = dt.astype(datetime.datetime)

        if isinstance(dt, datetime.datetime):
            return dt

        if isinstance(dt, datetime.date):
            return to_datetime(dt)

        if isinstance(dt, int):
            return datetime.datetime.utcfromtimestamp(dt * 1e-9)

        raise ValueError("Failed to convert numpy datetime {}".format((dt, type(dt))))

    if isinstance(dt, str):
        return parse_date(dt)

    if getattr(dt, "to_datetime", None) is None:
        dt = helper(dt)

    return to_datetime(dt.to_datetime())


def _mars_list(start, end, by):
    assert by > 0, by
    assert end >= start
    result = []
    while start <= end:
        result.append(start)
        start = start + datetime.timedelta(days=by)
    return result


def to_datetime_list(datetimes):  # noqa C901

    if isinstance(datetimes, str):
        # MARS style lists
        bits = datetimes.split("/")
        if len(bits) == 3 and bits[1].lower() == "to":
            return _mars_list(to_datetime(bits[0]), to_datetime(bits[2]), 1)

        if len(bits) == 5 and bits[1].lower() == "to" and bits[3].lower() == "by":
            return _mars_list(to_datetime(bits[0]), to_datetime(bits[2]), int(bits[4]))

        try:
            return to_datetime_list(bits)
        except Exception:
            pass

    if isinstance(datetimes, (datetime.datetime, np.datetime64, str)):
        return to_datetime_list([datetimes])

    if isinstance(datetimes, (list, tuple)):
        if (
            len(datetimes) == 3
            and isinstance(datetimes[1], str)
            and datetimes[1].lower() == "to"
        ):
            return _mars_list(to_datetime(datetimes[0]), to_datetime(datetimes[2]), 1)

        if (
            len(datetimes) == 5
            and datetimes[1].lower() == "to"
            and datetimes[3].lower() == "by"
        ):
            return _mars_list(
                to_datetime(datetimes[0]), to_datetime(datetimes[2]), int(datetimes[4])
            )

        return [to_datetime(x) for x in datetimes]

    if getattr(datetimes, "to_datetime_list", None) is None:
        datetimes = helper(datetimes)

    return to_datetime_list(datetimes.to_datetime_list())


def to_dates_and_times(datetimes_list):
    assert False, datetimes_list
    # result = []
    # datetimes = defaultdict(set)

    # for dt in to_datetime_list(datetimes_list):
    #     datetimes[dt.date())].add(dt.time())

    # timedates = defaultdict(set)
    # for date, times in sorted(datetimes.items()):
    #     times = tuple(sorted(times))
    #     timedates[times].add(date)

    # for times, dates in timedates.items():
    #     result.append((tuple(sorted(dates)), times))

    # return sorted(result)


def to_date_list(obj):
    return sorted(set(to_datetime_list(obj)))
