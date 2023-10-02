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
from copy import deepcopy
from functools import cached_property

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

            group_by = values.get("group_by")
            if group_by in ["monthly", "daily"]:
                values["type"] = values.get("type", "date")

            if values.get("type") == "date":
                start = to_datetime(start)
                stop = to_datetime(stop)
                step = datetime.timedelta(days=1)
                format = lambda x: x.isoformat() # noqa: E731
            else:
                step = values.get("step", 1)
                format = lambda x: x # noqa: E731

            all = []
            while start <= stop:
                all.append(start)
                start += step

            grouper = {
                None: lambda x: 0,  # only one group
                # None: lambda x: x, # one group per value
                "monthly": lambda dt: (dt.year, dt.month),
                "daily": lambda dt: (dt.year, dt.month, dt.day),
                "MMDD": lambda dt: (dt.month, dt.day),
            }[group_by]
            result = [list(g) for _, g in itertools.groupby(all, key=grouper)]
            return [[format(x) for x in g] for g in result]

    raise ValueError(f"Cannot expand loop from {values}")


class Config(DictObj):
    def __init__(self, config):
        if isinstance(config, str):
            self._config_path = config
            config = load_json_or_yaml(config)
        super().__init__(config)


def count_fields(request):
    dic = deepcopy(request)
    print(dic)
    product = 1
    for k, value in dic.items():
        if k in ["grid"]:
            continue

        if isinstance(value, str) and "/" in value:
            bits = value.split("/")
            if len(bits) == 3 and bits[1].lower() == "to":
                value = list(range(int(bits[0]), int(bits[2]) + 1, 1))

            elif len(bits) == 5 and bits[1].lower() == "to" and bits[3].lower() == "by":
                value = list(
                    range(int(bits[0]), int(bits[2]) + int(bits[4]), int(bits[4]))
                )

        if isinstance(value, list):
            product *= len(value)

    return product


class InputBlockLoadersConfig(list):
    loop = None

    def __init__(self, config):
        assert isinstance(config, list), config

        for elt in config:
            assert isinstance(elt, dict), elt
            assert len(elt) == 1
            only_key = list(elt.keys())[0]
            assert only_key in ["loop", "source", "constants", "inherit"], only_key
            if only_key == "loop":
                self.loop = elt["loop"]

        super().__init__(config)

    def iter_loops(self):
        if not self.loop:
            yield (self, {}, self._count(self))

        for items in itertools.product(expand(*list(self.loop.values()))):
            vars = dict(zip(self.loop.keys(), items))
            config = self.substitute(vars)
            length = self._count(config)

            import climetlab as cml

            data = cml.load_source("loader", config)
            print(data)
            exit()

        yield (config, vars, length)

    def _count(self, config):
        sum = 0
        for elt in config:
            if "loop" in elt:
                continue
            if "source" in elt:
                for s in elt["source"]:
                    print("counted", count_fields(s), " fields in ", s)
                    sum += count_fields(s)
        return sum

    @cached_property
    def n_iter_loops(self):
        return len([self.iter_loops()])

    def __repr__(self) -> str:
        return super().__repr__() + " Loop=" + str(self.loop)

    def get_first_config(self):
        for item in self.iter_loops():
            config = item[0]
            vars = item[1]
            keys = list(vars.keys())
            assert len(vars) == 1, (keys, "not implemented")
            return config

    def substitute(self, *args, **kwargs):
        self_without_loop = [i for i in self if "loop" not in i]
        return InputBlockLoadersConfig(substitute(self_without_loop, *args, **kwargs))

    # def get_first_and_last_configs(self):
    #     first = None
    #     for i, vars in enumerate(self.iter_loops()):
    #         keys = list(vars.keys())
    #         assert len(vars) == 1, keys
    #         key = keys[0]
    #         if first is None:
    #             first = self.main_config.substitute({key: vars[key][0]})
    #     last = self.main_config.substitute({key: vars[key][-1]})
    #     return first, last


class LoadersConfig(Config):
    def __init__(self, config, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        if not isinstance(self.input, list):
            print(f"warning: {self.input=} is not a list")
            self.input = [self.input]

        self.input = [InputBlockLoadersConfig(c) for c in self.input]

        if "order" in self.output:
            raise ValueError(f"Do not use 'order'. Use order_by in {config}")
        if "order_by" in self.output:
            self.output.order_by = normalize_order_by(self.output.order_by)

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

    def iter_loops(self):
        for block in self.input:
            yield from block.iter_loops()

    @cached_property
    def n_iter_loops(self):
        return sum([block.n_iter_loops for block in self.input])

    def substitute(self, *args, **kwargs):
        raise NotImplementedError()
        return Config(substitute(self, *args, **kwargs))


def substitute(x, vars=None, ignore_missing=False):
    """Recursively substitute environment variables and dict values in a nested list ot dict of string.
    substitution is performed using the environment var (if UPPERCASE) or the input dictionary.


    >>> substitute({'bar': '$bar'}, {'bar': '43'})
    {'bar': '43'}

    >>> substitute({'bar': '$BAR'}, {'BAR': '43'})
    Traceback (most recent call last):
        ...
    KeyError: 'BAR'

    >>> substitute({'bar': '$BAR'}, ignore_missing=True)
    {'bar': '$BAR'}

    >>> os.environ["BAR"] = "42"
    >>> substitute({'bar': '$BAR'})
    {'bar': '42'}

    >>> substitute('$bar', {'bar': '43'})
    '43'

    >>> substitute('$hdates_from_date($date, 2015, 2018)', {'date': '2023-05-12'})
    '2015-05-12/2016-05-12/2017-05-12/2018-05-12'

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

        for i, bit in enumerate(re.split(r"(\$(\w+)(\([^\)]*\))?)", x)):
            i %= 4
            if i in [2, 3]:
                continue
            if i == 1:
                try:
                    if "(" in bit:
                        # substitute by a function
                        FUNCTIONS = dict(hdates_from_date=hdates_from_date)

                        pattern = r"\$(\w+)\(([^)]*)\)"
                        match = re.match(pattern, bit)
                        assert match, bit

                        function_name = match.group(1)
                        params = [p.strip() for p in match.group(2).split(",")]
                        params = [
                            substitute(p, vars, ignore_missing=ignore_missing)
                            for p in params
                        ]

                        bit = FUNCTIONS[function_name](*params)

                    elif bit.upper() == bit:
                        # substitute by the var env if $UPPERCASE
                        bit = os.environ[bit[1:]]
                    else:
                        # substitute by the value in the 'vars' dict
                        bit = vars[bit[1:]]
                except KeyError as e:
                    if not ignore_missing:
                        raise e

            if bit != x:
                bit = substitute(bit, vars, ignore_missing=ignore_missing)

            lst.append(bit)

        lst = [_ for _ in lst if _ != ""]
        if len(lst) == 1:
            return lst[0]

        out = []
        for elt in lst:
            # if isinstance(elt, str):
            #    elt = [elt]
            assert isinstance(elt, (list, tuple)), elt
            out += elt
        return out

    return x


def hdates_from_date(date, start_year, end_year):
    """
    Returns a list of dates in the format '%Y%m%d' between start_year and end_year (inclusive),
    with the year of the input date.

    Args:
        date (str or datetime): The input date.
        start_year (int): The start year.
        end_year (int): The end year.

    Returns:
        List[str]: A list of dates in the format '%Y%m%d'.
    """
    if not str(start_year).isdigit():
        raise ValueError(f"start_year must be an int: {start_year}")
    if not str(end_year).isdigit():
        raise ValueError(f"end_year must be an int: {end_year}")
    start_year = int(start_year)
    end_year = int(end_year)

    from climetlab.utils.dates import to_datetime

    if isinstance(date, (list, tuple)):
        raise NotImplementedError(f"{date}")

    date = to_datetime(date)
    assert not (date.hour or date.minute or date.second), date

    hdates = [date.replace(year=year) for year in range(start_year, end_year + 1)]
    return "/".join(d.strftime("%Y-%m-%d") for d in hdates)
