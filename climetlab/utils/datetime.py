# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from collections import defaultdict
import datetime
from dateutil.parser import parse

# datetime.fromisoformat() only available from Python3.7
from backports.datetime_fromisoformat import MonkeyPatch

MonkeyPatch.patch_fromisoformat()


def parse_date(date):
    return datetime.datetime.fromisoformat(date)


def to_datetime(dt):
    if isinstance(dt, datetime.datetime):
        return dt

    if isinstance(dt, str):
        return parse(dt)

    raise Exception("Unsupported date/time object %s (%s)" % (dt, type(dt)))


def to_datetimes_list(datetimes):
    if isinstance(datetimes, (datetime.datetime, str)):
        return to_datetimes_list([datetimes])

    if isinstance(datetimes, (list, tuple)):
        return [to_datetime(x) for x in datetimes]

    return datetimes


def _date_as_request(date):
    return "%d-%02d-%02d" % (date.year, date.month, date.day)


def _time_as_request(time):
    assert time.second == 0
    return "%02d:%02d" % (time.hour, time.minute)


def _indentity(x):
    return x


def datetimes_to_dates_and_times(datetimes_list, as_request=False):

    result = []
    datetimes = defaultdict(set)

    if as_request:
        _d = _date_as_request
        _t = _time_as_request
    else:
        _d = _indentity
        _t = _indentity

    for dt in to_datetimes_list(datetimes_list):
        datetimes[_d(dt.date())].add(_t(dt.time()))

    timedates = defaultdict(set)
    for date, times in sorted(datetimes.items()):
        times = tuple(sorted(times))
        timedates[times].add(date)

    for times, dates in timedates.items():
        result.append((tuple(sorted(dates)), times))

    return sorted(result)
