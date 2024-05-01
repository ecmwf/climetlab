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
from climetlab.core.temporary import temp_file
from climetlab.decorators import normalize
from climetlab.readers.grib.output import new_grib_output
from climetlab.utils.availability import Availability


class Accumulation:
    def __init__(self, out, param, date, time, step, number, stepping):
        self.out = out
        self.param = param
        self.date = date
        self.time = time * 100
        self.number = number
        self.steps = tuple(step)
        self.values = None
        self.seen = set()
        self.startStep = None
        self.endStep = None
        self.done = False
        self.stepping = stepping

    @property
    def key(self):
        return (self.param, self.date, self.time, self.steps, self.number)

    def add(self, field, values):
        step = field.metadata("step")
        if step not in self.steps:
            return

        assert not self.done, (self.key, step)

        startStep = field.metadata("startStep")
        endStep = field.metadata("endStep")

        assert endStep == step, (startStep, endStep, step)
        assert step not in self.seen, (self.key, step)

        assert endStep - startStep == self.stepping, (startStep, endStep)

        if self.startStep is None:
            self.startStep = startStep
        else:
            self.startStep = min(self.startStep, startStep)

        if self.endStep is None:
            self.endStep = endStep
        else:
            self.endStep = max(self.endStep, endStep)

        if self.values is None:
            import numpy as np

            self.values = np.zeros_like(values)

        self.values += values

        self.seen.add(step)

        if len(self.seen) == len(self.steps):
            self.out.write(
                self.values,
                template=field,
                startStep=self.startStep,
                endStep=self.endStep,
            )
            self.values = None
            self.done = True


class Era5Accumulations(Source):
    """This source use a MARS request to get the data for accumulated fields
    following the same logic as what has been done when storing ERA5 in the
    Climate Data Store (CDS).
    The date+time provided to this source refers to the valid datetime of the data,
    these date+time are used to compute the date+time+step that are actually used to perform the mars request.

    Note 1 : as all these are lists, there are potentially to many fields requested to MARS.
          This is taken care by the final ".sel" .
    Note 2 : There are no overlap due to the way the date+time+step are computed
    """

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

        number = request.get("number", [0])
        assert isinstance(number, (list, tuple))

        user_step = 6  # For now, we only support 6h accumulation

        user_dates = request["date"]
        user_times = request["time"]

        requested = set()

        era_request = dict(**request)

        type_ = request.get("type", "an")
        if type_ == "an":
            type_ = "fc"

        stepping = 1
        if request.get("stream") == "enda":
            stepping = 3
            for n in user_times:
                assert n % 6 == 0, n

        era_request.update({"class": "ea", "type": type_, "levtype": "sfc"})

        tmp = temp_file()
        path = tmp.path
        out = new_grib_output(path)

        requests = []

        for user_date, user_time in itertools.product(user_dates, user_times):
            assert isinstance(user_date, datetime.datetime), (
                type(user_date),
                user_dates,
                user_times,
            )
            assert isinstance(user_time, int), (type(user_time), user_dates, user_times)
            assert 0 <= user_time <= 24, user_time

            requested.add(user_date + datetime.timedelta(hours=user_time))

            when = (
                user_date
                + datetime.timedelta(hours=user_time)
                - datetime.timedelta(hours=user_step)
            )
            add_step = 0

            while when.hour not in (6, 18):
                when -= datetime.timedelta(hours=stepping)
                add_step += stepping

            steps = tuple(
                step + add_step
                for step in range(stepping, user_step + stepping, stepping)
            )

            for p in param:
                for n in number:
                    requests.append(
                        {
                            "param": p,
                            "date": int(when.strftime("%Y%m%d")),
                            "time": when.hour,
                            "step": sorted(steps),
                            "number": n,
                        }
                    )

        compressed = Availability(requests)
        ds = cml.load_source("empty")
        for r in compressed.iterate():
            era_request.update(r)
            ds = ds + cml.load_source("mars", **era_request)

        accumulations = defaultdict(list)
        for a in [Accumulation(out, stepping=stepping, **r) for r in requests]:
            for s in a.steps:
                accumulations[(a.param, a.date, a.time, s, a.number)].append(a)

        for field in ds:
            key = (
                field.metadata("param"),
                field.metadata("date"),
                field.metadata("time"),
                field.metadata("step"),
                field.metadata("number"),
            )
            values = field.values  # optimisation
            for a in accumulations[key]:
                a.add(field, values)

        for acc in accumulations.values():
            for a in acc:
                assert a.done, (a.key, a.seen, a.steps)

        out.close()

        ds = cml.load_source("file", path)

        self.ds = cml.load_source("file", path)
        assert len(self.ds) / len(param) / len(number) == len(requested), (
            len(self.ds),
            len(param),
            len(requested),
        )
        self.ds._tmp = tmp

    def mutate(self):
        return self.ds

    @normalize("date", "date-list(datetime.datetime)")
    @normalize("time", "int-list")
    @normalize("area", "bounding-box(list)")
    def requests(self, **kwargs):
        result = dict(**kwargs)

        return result


source = Era5Accumulations
