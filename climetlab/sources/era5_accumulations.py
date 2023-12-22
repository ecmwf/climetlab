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

        user_step = 6  # For now, we only support 6h accumulation
        user_dates = request["date"]
        user_times = request["time"]

        requested = set()

        dates = set()
        times = set()
        steps = set()

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
                when -= datetime.timedelta(hours=1)
                add_step += 1

            dates.add(datetime.datetime(when.year, when.month, when.day))
            times.add(when.hour)
            for step in range(1, user_step + 1):
                steps.add(step + add_step)

        valids = defaultdict(list)
        for date, time, step in itertools.product(dates, times, steps):
            valids[
                date + datetime.timedelta(hours=time) + datetime.timedelta(hours=step)
            ].append((date, time, step))

        got = set(valids.keys())
        assert all(len(x) == 1 for x in valids.values())
        missing = requested - got
        assert len(missing) == 0, missing

        # extra = got - requested

        era_request = dict(**request)

        type_ = request.get("type", "an")
        if type_ == "an":
            type_ = "fc"

        era_request.update(
            {
                "class": "ea",
                "type": type_,
                "levtype": "sfc",
                "date": [d.strftime("%Y-%m-%d") for d in dates],
                "time": sorted(times),
                "step": sorted(steps),
            }
        )

        ds = cml.load_source("mars", **era_request)

        ds = ds.order_by("param", "date", "time", "step")
        last_key = None
        fields = []

        tmp = temp_file()
        path = tmp.path
        out = new_grib_output(path)

        def flush():
            nonlocal last_key, fields
            if last_key is None:
                return
            lastStep = None
            values = None
            startSteps = []
            endSteps = []
            for field in fields:
                startStep = field.metadata("startStep")
                endStep = field.metadata("endStep")
                startSteps.append(startStep)
                endSteps.append(endStep)
                if lastStep is not None:
                    assert startStep == lastStep
                assert endStep - startStep == 1, (startStep, endStep)
                lastStep = endStep
                if values is None:
                    values = field.values
                else:
                    values += field.values

            out.write(
                values,
                template=fields[0],
                startStep=min(startSteps),
                endStep=max(endSteps),
            )

            fields = []

        for field in ds:
            key = (
                field.metadata("param"),
                field.metadata("date"),
                field.metadata("time"),
            )
            step = field.metadata("step")
            if key != last_key:
                flush()
                last_key = key

            fields.append(field)

        flush()
        out.close()

        ds = cml.load_source("file", path)

        index = [d.valid_datetime() in requested for d in ds]
        self.ds = ds[index]
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
