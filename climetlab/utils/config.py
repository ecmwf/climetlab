# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import itertools
import logging
import os
import re
import datetime

from climetlab.core.order import build_remapping, normalize_order_by
from climetlab.utils import load_json_or_yaml

LOG = logging.getLogger(__name__)


def expand(values):
    if isinstance(values, list):
        return values

    if isinstance(values, dict):
        if "start" in values and "stop" in values:
            start = values["start"]
            stop = values["stop"]
            step = values.get("step", 1)
            return range(start, stop + 1, step)

        if "monthly" in values:
            start = values["monthly"]["start"]
            stop = values["monthly"]["stop"]
            date = start
            last = None
            result = []
            lst = []
            while True:
                year, month = date.year, date.month
                if (year, month) != last:
                    if lst:
                        result.append([d.isoformat() for d in lst])
                    lst = []

                lst.append(date)
                last = (year, month)
                date = date + datetime.timedelta(days=1)
                if date > stop:
                    break
            if lst:
                result.append([d.isoformat() for d in lst])
            return result

    raise ValueError(f"Cannot expand loop from {values}")


class Config:
    def __init__(self, config, **kwargs):
        if isinstance(config, str):
            config = load_json_or_yaml(config)
        self.config = config
        self.input = config["input"]
        self.output = config["output"]
        self.constants = config.get("constants")
        if "order" in self.output:
            self.order = normalize_order_by(self.output["order"])
        self.remapping = build_remapping(self.output.get("remapping"))

        self.loop = self.config.get("loop")
        self.extra = self.config.get("extra")
        self.chunking = self.output.get("chunking", {})
        self.dtype = self.output.get("dtype", "float32")

        self.reading_chunks = config.get("reading_chunks")
        self.flatten_values = self.output.get("flatten_values", False)
        self.grid_points_first = self.output.get("grid_points_first", False)
        if self.grid_points_first and not self.flatten_values:
            raise NotImplementedError(
                "For now, grid_points_first is only valid if flatten_values"
            )

        # The axis along which we append new data
        # TODO: assume grid points can be 2d as well
        self.append_axis = 1 if self.grid_points_first else 0

        self.collect_statistics = False
        if "statistics" in self.output:
            statistics_axis_name = self.output["statistics"]
            statistics_axis = -1
            for i, k in enumerate(self.order):
                if k == statistics_axis_name:
                    statistics_axis = i

            assert statistics_axis >= 0, (statistics_axis_name, self.order)

            self.statistics_names = self.order[statistics_axis_name]

            # TODO: consider 2D grid points
            self.statistics_axis = (
                statistics_axis + 1 if self.grid_points_first else statistics_axis
            )
            self.collect_statistics = True

    def _iter_loops(self):
        # see also iter_configs
        yield from (
            dict(zip(self.loop.keys(), items))
            for items in itertools.product(
                expand(*list(self.loop.values())),
            )
        )

    def iter_configs(self):
        if self.loop is None:
            return [self]

        for items in itertools.product(
            expand(*list(self.loop.values())),
        ):
            vars = dict(zip(self.loop.keys(), items))
            yield (vars, self.substitute(vars))

    def substitute(self, vars):
        def substitute(x, vars):
            if isinstance(x, (tuple, list)):
                return [substitute(y, vars) for y in x]

            if isinstance(x, dict):
                return {k: substitute(v, vars) for k, v in x.items()}

            if isinstance(x, str):
                if not re.match(r"\$(\w+)", x):
                    return x
                lst = []
                for i, bit in enumerate(re.split(r"\$(\w+)", x)):
                    if i % 2:
                        if bit.upper() == bit:
                            # substitute by the var env if $UPPERCASE
                            lst.append(os.environ[bit])
                        else:
                            # substitute by the value in the 'vars' dict
                            lst.append(vars[bit])
                    else:
                        lst.append(bit)

                lst = [e for e in lst if e != ""]

                if len(lst) == 1:
                    return lst[0]

                return "".join(str(_) for _ in lst)

            return x

        return Config(substitute(self.config, vars))
