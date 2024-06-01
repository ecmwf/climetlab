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

import climetlab as cml
from climetlab import Source
from climetlab.decorators import normalize


class OperAccumulations(Source):
    def __init__(self, *args, **kwargs):
        request = {}
        for a in args:
            request.update(self.requests(**a))
        request = self.requests(**kwargs)

        param = request["param"]

        if not isinstance(param, (list, tuple)):
            param = [param]

        for p in param:
            assert p in ["cp", "lsp", "tp"], p

        user_dates = request["date"]
        user_times = request["time"]

        requests = {
            "oper": {"dates": set(), "times": set()},
            "scda": {"dates": set(), "times": set()},
        }

        user_step = 6
        requested = set()

        for user_date, user_time in itertools.product(user_dates, user_times):
            assert isinstance(user_date, datetime.datetime), (
                type(user_date),
                user_dates,
                user_times,
            )
            assert isinstance(user_time, int), (type(user_time), user_dates, user_times)
            assert user_time in [0, 6, 12, 18], user_time

            when = user_date + datetime.timedelta(hours=user_time)

            requested.add(when)

            when -= datetime.timedelta(hours=user_step)
            date = datetime.datetime(when.year, when.month, when.day)
            time = when.hour

            stream = {0: "oper", 6: "scda", 12: "oper", 18: "scda"}[time]
            requests[stream]["dates"].add(date)
            requests[stream]["times"].add(time)
            print(requests)

        dataset = dict(oper=cml.load_source("empty"), scda=cml.load_source("empty"))

        for stream in ["oper", "scda"]:
            dates = sorted(requests[stream]["dates"])
            times = sorted(requests[stream]["times"])

            if not dates and not times:
                continue

            assert dates, (stream, dates, times)

            oper_request = dict(**request)

            oper_request.update(
                {
                    "class": "od",
                    "type": "fc",
                    "levtype": "sfc",
                    "stream": stream,
                    "date": [d.strftime("%Y-%m-%d") for d in dates],
                    "time": sorted(times),
                    "step": user_step,
                }
            )

            ds = cml.load_source("mars", **oper_request)
            index = [d.valid_datetime() in requested for d in ds]
            dataset[stream] = ds[index]

        self.ds = dataset["oper"] + dataset["scda"]

    def mutate(self):
        return self.ds

    @normalize("date", "date-list(datetime.datetime)")
    @normalize("time", "int-list")
    @normalize("area", "bounding-box(list)")
    def requests(self, **kwargs):
        result = dict(**kwargs)

        return result


source = OperAccumulations
