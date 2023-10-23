# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import itertools
from collections import defaultdict

import climetlab as cml
from climetlab import Source
from climetlab.decorators import normalize

mapping = [
    [-1, 18, 6],
    [-1, 18, 7],
    [-1, 18, 8],
    [-1, 18, 9],
    [-1, 18, 10],
    [-1, 18, 11],
    [-1, 18, 12],
    [0, 6, 1],
    [0, 6, 2],
    [0, 6, 3],
    [0, 6, 4],
    [0, 6, 5],
    [0, 6, 6],
    [0, 6, 7],
    [0, 6, 8],
    [0, 6, 9],
    [0, 6, 10],
    [0, 6, 11],
    [0, 6, 12],
    [0, 18, 1],
    [0, 18, 2],
    [0, 18, 3],
    [0, 18, 4],
    [0, 18, 5],
]


class Era5Accumulations(Source):
    def __init__(self, *args, **kwargs):
        request = self.requests(**kwargs)

        user_dates = request["date"]
        user_times = request["time"]

        requested = set()

        dates = set()
        times = set()
        steps = set()

        for user_date, user_time in itertools.product(user_dates, user_times):
            date = user_date + datetime.timedelta(hours=user_time)
            delta, time, step = mapping[date.hour]
            when = date + datetime.timedelta(days=delta)
            dates.add(datetime.datetime(when.year, when.month, when.day))
            times.add(time)
            steps.add(step)
            requested.add(date)

        valids = defaultdict(list)
        for date, time, step in itertools.product(dates, times, steps):
            valids[
                date + datetime.timedelta(hours=time) + datetime.timedelta(hours=step)
            ].append((date, time, step))

        got = set(valids.keys())
        assert all(len(x) == 1 for x in valids.values())
        missing = requested - got
        assert len(missing) == 0

        # extra = got - requested

        era_request = dict(**request)

        era_request.update(
            {
                "class": "ea",
                "type": "fc",
                "levtype": "sfc",
                "date": [d.strftime("%Y-%m-%d") for d in dates],
                "time": sorted(times),
                "step": sorted(steps),
            }
        )

        ds = cml.load_source("mars", **era_request)
        index = [d.valid_datetime() in requested for d in ds]
        self.ds = ds[index]

    def mutate(self):
        return self.ds

    @normalize("date", "date-list(%Y-%m-%d)")
    @normalize("area", "bounding-box(list)")
    def requests(self, **kwargs):
        result = dict(**kwargs)

        return result


source = Era5Accumulations
