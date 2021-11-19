# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime

import numpy as np

from climetlab.wrappers import get_wrapper


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

    dt = get_wrapper(dt)

    return to_datetime(dt.to_datetime())


def mars_like_date_list(start, end, by):
    """Return a list of datetime objects from start to end .

    Parameters
    ----------
    start : [type]
        [description]
    end : [type]
        [description]
    by : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    assert by > 0, by
    assert end >= start
    result = []
    while start <= end:
        result.append(start)
        start = start + datetime.timedelta(days=by)
    return result


def to_datetime_list(datetimes):  # noqa C901

    if isinstance(datetimes, (datetime.datetime, np.datetime64)):
        return to_datetime_list([datetimes])

    if isinstance(datetimes, (list, tuple)):
        if (
            len(datetimes) == 3
            and isinstance(datetimes[1], str)
            and datetimes[1].lower() == "to"
        ):
            return mars_like_date_list(
                to_datetime(datetimes[0]), to_datetime(datetimes[2]), 1
            )

        if (
            len(datetimes) == 5
            and datetimes[1].lower() == "to"
            and datetimes[3].lower() == "by"
        ):
            return mars_like_date_list(
                to_datetime(datetimes[0]), to_datetime(datetimes[2]), int(datetimes[4])
            )

        return [to_datetime(x) for x in datetimes]

    datetimes = get_wrapper(datetimes)

    return to_datetime_list(datetimes.to_datetime_list())


def to_date_list(obj):
    return sorted(set(to_datetime_list(obj)))
