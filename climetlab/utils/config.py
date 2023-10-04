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


class InputConfigs(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in self:
            i.process_inheritance(self)

    def substitute(self, *args, **kwargs):
        new = [i.substitute(*args, **kwargs) for i in self]
        return InputConfigs(new)


class InputConfig(dict):
    loop = None
    _inheritance_done = False

    def __init__(self, dic):
        assert isinstance(dic, dict), dic
        assert len(dic) == 1
        super().__init__(dic)

        self.name = list(dic.keys())[0]
        self.config = dic[self.name]

        self.kwargs = self.config.get("kwargs", {})
        self.inherit = self.config.get("inherit", [])

        import climetlab as cml

        self.func = cml.load_source

    def process_inheritance(self, others):
        for o in others:
            if o == self:
                continue
            name = o.name
            if name.startswith("$"):
                name = name[1:]
            if name not in self.inherit:
                continue
            if not o._inheritance_done:
                o.process_inheritance(others)

            kwargs = {}
            kwargs.update(o.kwargs)
            kwargs.update(self.kwargs)  # self.kwargs has priority
            self.kwargs = kwargs

        self._inheritance_done = True

    def __repr__(self) -> str:
        def repr(v):
            if isinstance(v, list):
                return f"{'/'.join(str(x) for x in v)}"
            return str(v)

        details = ", ".join(f"{k}={repr(v)}" for k, v in self.kwargs.items())
        return f"InputConfig({self.name}, {details})<{self.inherit}"

    def substitute(self, *args, **kwargs):
        return InputConfig(substitute(self, *args, **kwargs))

    # def iter_loops(self):
    #    if not self.loop:
    #        yield (self, {}, self._count(self))

    #    for items in itertools.product(expand(*list(self.loop.values()))):
    #        vars = dict(zip(self.loop.keys(), items))
    #        config = self.substitute(vars)
    #        length = self._count(config)

    #        import climetlab as cml


#   #         data = cml.load_source("loader", config)
#   #         print(data)

#    yield (config, vars, length)

# def _count(self, config):
#    sum = 0
#    for elt in config:
#        if "loop" in elt:
#            continue
#        if "source" in elt:
#            for s in elt["source"]:
#

#   #                 print("counted", count_fields(s), " fields in ", s)
#                sum += count_fields(s)
#    return sum

# @cached_property
# def n_iter_loops(self):
#    return len([self.iter_loops()])

# def __repr__(self) -> str:
#    return super().__repr__() + " Loop=" + str(self.loop)

# def get_first_config(self):
#    for item in self.iter_loops():
#        config = item[0]
#        vars = item[1]
#        keys = list(vars.keys())
#        assert len(vars) == 1, (keys, "not implemented")
#        return config

# def substitute(self, *args, **kwargs):
#    self_without_loop = [i for i in self if "loop" not in i]
#    return InputConfig(substitute(self_without_loop, *args, **kwargs))

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


class Loops(list):
    def iterate(self):
        if not self:
            # TODO: if no loop, we should return the config as is
            yield CubeCreator({})

        for loop in self:
            yield from loop.iterate()


class Loop(dict):
    def __init__(self, dic, inputs):
        assert isinstance(dic, dict), dic
        assert len(dic) == 1, dic
        super().__init__(dic)

        self.name = list(dic.keys())[0]
        self.config = dic[self.name]

        applies_to = self.config.pop("applies_to")
        self.applies_to_inputs = InputConfigs(
            input for input in inputs if input.name in applies_to
        )

        self.values = {}
        for k, v in self.config.items():
            self.values[k] = self.expand(v)

    def expand(self, values):
        return expand(values)

    def __repr__(self) -> str:
        def repr_lengths(v):
            return f"{','.join([str(len(x)) for x in v])}"

        lenghts = [f"{k}({repr_lengths(v)})" for k, v in self.values.items()]
        return f"Loop({self.name}, {','.join(lenghts)}) {self.config}"

    def iterate(self):
        for items in itertools.product(*self.values.values()):
            vars = dict(zip(self.values.keys(), items))
            yield CubeCreator(
                inputs=self.applies_to_inputs, vars=vars, loop_config=self.config
            )


class CubeCreator:
    def __init__(self, inputs, vars, loop_config):
        self._loop_config = loop_config
        self._vars = vars
        self._inputs = inputs

        self.inputs = inputs.substitute(vars=vars, ignore_missing=True)

    @property
    def length(self):
        return 1

    def __repr__(self) -> str:
        out = f"CubeCreator ({self.length}):\n"
        out += f" loop_config: {self._loop_config}"
        out += f" vars: {self._vars}\n"
        out += f" Inputs:\n"
        for _i, i in zip(self._inputs, self.inputs):
            out += f"  {_i}\n"
            out += f"->{i}\n"
        return out

    def load(self):
        pass


class LoadersConfig(Config):
    def __init__(self, config, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        if not isinstance(self.input, list):
            print(f"warning: {self.input=} is not a list")
            self.input = [self.input]

        self.input = InputConfigs(InputConfig(c) for c in self.input)
        for i in self.input:
            print(i)

        self.loops = Loops(Loop(l, self.input) for l in self.loops)
        for l in self.loops:
            print(l)

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
        return self.loops.iterate()

    @cached_property
    def n_iter_loops(self):
        return sum([loop.n_iter_loops for loop in self.loops])


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


class Expand(list):
    def __init__(self, config, **kwargs):
        self._config = config
        self.kwargs = kwargs
        self.groups = []
        self.parse_config()

    def parse_config(self):
        self.start = self._config.get("start")
        self.stop = self._config.get("stop")
        self.step = self._config.get("step", 1)
        self.group_by = self._config.get("group_by")


class HindcastExpand(Expand):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.groups = [["todo", "todo"]]


class ValuesExpand(Expand):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        values = self._config["values"]
        values = [[v] if not isinstance(v, list) else v for v in values]
        for v in self._config["values"]:
            if not isinstance(v, (tuple, list)):
                v = [v]
            self.groups.append(v)


class StartStopExpand(Expand):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

        x = self.start
        all = []
        while x <= self.stop:
            all.append(x)
            x += self.step

        result = [list(g) for _, g in itertools.groupby(all, key=self.grouper_key)]
        self.groups = [[format(x) for x in g] for g in result]

    def parse_config(self):
        if "end" in self._config:
            raise ValueError(f"Use 'stop' not 'end' in loop. {self._config}")
        super().parse_config()

    def format(self, x):
        return x


class DateStartStopExpand(StartStopExpand):
    def grouper_key(self, x):
        return {
            1: lambda x: 0,  # only one group
            None: lambda x: x,  # one group per value
            "monthly": lambda dt: (dt.year, dt.month),
            "daily": lambda dt: (dt.year, dt.month, dt.day),
            "MMDD": lambda dt: (dt.month, dt.day),
        }[self.group_by](x)

    def parse_config(self):
        super().parse_config()
        assert isinstance(self.start, datetime.date), (type(self.start), self.start)
        assert isinstance(self.stop, datetime.date), (type(self.stop), self.stop)
        self.step = datetime.timedelta(days=self.step)

    def format(self, x):
        return x.isoformat()


class IntStartStopExpand(StartStopExpand):
    def grouper_key(self, x):
        return {
            1: lambda x: 0,  # only one group
            None: lambda x: x,  # one group per value
        }[self.group_by](x)


def _expand_class(values):
    if isinstance(values, list):
        return ValuesExpand

    assert isinstance(values, dict), values

    if values.get("type") == "hindcast":
        return HindcastExpand

    if start := values.get("start"):
        if isinstance(start, datetime.datetime):
            return DateStartStopExpand
        if values.get("group_by") in ["monthly", "daily"]:
            return DateStartStopExpand
        return IntStartStopExpand

    raise ValueError(f"Cannot expand loop from {values}")


def expand(values, **kwargs):
    cls = _expand_class(values)
    return cls(values, **kwargs).groups
