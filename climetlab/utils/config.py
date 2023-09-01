# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import datetime
import itertools
import logging
import os
import re

from climetlab.core.order import build_remapping, normalize_order_by
from climetlab.utils import load_json_or_yaml

LOG = logging.getLogger(__name__)


class DictObj(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = DictObj(value)
                continue
            if isinstance(value, list):
                self[key] = [
                    DictObj(item) if isinstance(item, dict) else item for item in value
                ]
                continue

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        self[attr] = value


def expand(values):
    from climetlab.utils.dates import to_datetime

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

            start = to_datetime(start)
            stop = to_datetime(stop)

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

        if "daily" in values:
            start = values["daily"]["start"]
            stop = values["daily"]["stop"]
            start = to_datetime(start)
            stop = to_datetime(stop)
            date = start
            result = []
            while True:
                result.append(date)
                date = date + datetime.timedelta(days=1)
                if date > stop:
                    break
            result = [d.isoformat() for d in result]
            return result

    raise ValueError(f"Cannot expand loop from {values}")


class Config(DictObj):
    def __init__(self, config):
        if isinstance(config, str):
            self._config_path = config
            config = load_json_or_yaml(config)
        super().__init__(config)

    def _iter_loops(self):
        # see also iter_configs
        yield from (
            dict(zip(self.loop.keys(), items))
            for items in itertools.product(
                expand(*list(self.loop.values())),
            )
        )

    def _len_of_iter_loops(self):
        n = 0
        for _ in self._iter_loops():
            n += 1
        return n

    def iter_configs(self):
        if self.loop is None:
            return [self]

        for items in itertools.product(
            expand(*list(self.loop.values())),
        ):
            vars = dict(zip(self.loop.keys(), items))
            yield (vars, self.substitute(vars))

    def substitute(self, *args, **kwargs):
        return Config(substitute(self, *args, **kwargs))


class LoadersConfig(Config):
    def __init__(self, config, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        if "order" in self.output:
            raise ValueError(f"Do not use 'order'. Use order_by in {config}")
        if "order_by" in self.output:
            self.output.order_by = normalize_order_by(self.output.order_by)

        if "constants" in self.input:
            self.input.constants = self.input["constants"]
        self.output.remapping = self.output.get("remapping", {})
        self.output.remapping = build_remapping(self.output.remapping)

        self.output.chunking = self.output.get("chunking", {})
        self.output.dtype = self.output.get("dtype", "float32")

        self.reading_chunks = self.get("reading_chunks")
        self.output.flatten_values = self.output.get("flatten_values", False)

        # The axis along which we append new data
        # TODO: assume grid points can be 2d as well
        self.output.append_axis = 0

        assert "statistics" in self.output
        statistics_axis_name = self.output.statistics
        statistics_axis = -1
        for i, k in enumerate(self.output.order_by):
            if k == statistics_axis_name:
                statistics_axis = i

        assert (
            statistics_axis >= 0
        ), f"{self.output.statistics} not in {list(self.output.order_by.keys())}"

        self.statistics_names = self.output.order_by[statistics_axis_name]

        # TODO: consider 2D grid points
        self.statistics_axis = statistics_axis


def substitute(x, vars=None, ignore_missing=False):
    """Recursively substitute environment variables and dict values in a nested list ot dict of string.
    substitution is performed using the environment var (if UPPERCASE) or the input dictionary.

    >>> substitute({'bar': '$bar'}, {'bar': '43'})
    {'bar': '43'}

    >>> substitute({'bar': '$BAR'}, {'BAR': '43'})
    Traceback (most recent call last):
        ...
    KeyError: 'BAR'

    >>> substitute({'bar': '$BAR'}, skip_missing=True)
    {'bar': '$BAR'}

    >>> os.environ["BAR"] = "42"
    >>> substitute({'bar': '$BAR'})
    {'bar': '42'}

    """
    if vars is None:
        vars = {}
    if isinstance(x, (tuple, list)):
        return [substitute(y, vars, ignore_missing=ignore_missing) for y in x]

    if isinstance(x, dict):
        return {
            k: substitute(v, vars, ignore_missing=ignore_missing) for k, v in x.items()
        }

    if isinstance(x, str):
        if "$" not in x:
            return x

        lst = []
        for i, bit in enumerate(re.split(r"\$(\w+)", x)):
            if i % 2:
                try:
                    if bit.upper() == bit:
                        # substitute by the var env if $UPPERCASE
                        bit = os.environ[bit]
                    else:
                        # substitute by the value in the 'vars' dict
                        bit = vars[bit]
                except KeyError as e:
                    if not ignore_missing:
                        raise e

            bit = substitute(bit, vars, ignore_missing=ignore_missing)

            lst.append(bit)

        lst = [e for e in lst if e != ""]

        if len(lst) == 1:
            return lst[0]

        return "".join(str(_) for _ in lst)

    return x
