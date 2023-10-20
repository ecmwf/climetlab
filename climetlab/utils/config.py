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
import math
import os
import re
import time
from copy import deepcopy
from functools import cached_property

import numpy as np

from climetlab.core.order import build_remapping, normalize_order_by
from climetlab.utils import load_json_or_yaml
from climetlab.utils.humanize import seconds

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


class Inputs(list):
    def __init__(self, args):
        assert isinstance(args[0], (dict, Input)), args[0]
        args = [c if isinstance(c, Input) else Input(c) for c in args]
        super().__init__(args)

    def substitute(self, *args, **kwargs):
        return Inputs([i.substitute(*args, **kwargs) for i in self])

    def get_datetimes(self):
        # get datetime from each input
        # and make sure they are the same or None
        datetimes = None
        previous_name = None
        for i in self:
            new = i.get_datetimes()
            if new is None:
                continue
            new = sorted(list(new))
            if datetimes is None:
                datetimes = new

            if datetimes != new:
                raise ValueError(
                    "Mismatch in datetimes", previous_name, datetimes, i.name, new
                )
            previous_name = i.name

        if datetimes is None:
            raise ValueError(f"No datetimes found in {self}")

        return datetimes

    def do_load(self):
        datasets = {}
        for i in self:
            i = i.substitute(vars=datasets)
            ds = i.do_load()
            datasets[i.name] = ds

        out = None
        for ds in datasets.values():
            if out is None:
                out = ds
            else:
                out += ds

        from climetlab.readers.grib.index import FieldSet

        assert isinstance(out, FieldSet), type(out)

        return out

    def __repr__(self) -> str:
        return "\n".join(str(i) for i in self)


class Input:
    _inheritance_done = False
    _inheritance_others = None
    _do_load = None

    def __init__(self, dic):
        assert isinstance(dic, dict), dic
        assert len(dic) == 1, dic

        self.name = list(dic.keys())[0]
        self.config = dic[self.name]

        if self.name == "forcing" or self.name == "constants":
            if "source_or_dataset" in self.config:
                # add $ to source_or_dataset for constants source.
                # climetlab will be refactored to remove this.
                assert self.config["source_or_dataset"][0] != "$", self.config[
                    "source_or_dataset"
                ]
                self.config["source_or_dataset"] = (
                    "$" + self.config["source_or_dataset"]
                )

        self.kwargs = self.config.get("kwargs", {})
        self.inherit = self.config.get("inherit", [])
        self.function = self.config.get("function", None)

    def get_datetimes(self, others={}):
        name = self.kwargs.get("name", None)

        assert name in ["constants", "mars"], f"{name} not implemented"

        if name == "constants":
            return None

        if name == "mars":
            is_hindast = "hdate" in self.kwargs

            date = self.kwargs.get("date", [])
            hdate = self.kwargs.get("hdate", [])
            time = self.kwargs.get("time", [0])
            step = self.kwargs.get("step", [0])

            from climetlab.utils.dates import to_datetime_list

            date = to_datetime_list(date)
            hdate = to_datetime_list(hdate)
            time = make_list_int(time)
            step = make_list_int(step)

            assert isinstance(date, (list, tuple)), date
            assert isinstance(time, (list, tuple)), time
            assert isinstance(step, (list, tuple)), step

            if is_hindast:
                assert isinstance(hdate, (list, tuple)), hdate
                if len(date) > 1 and len(hdate) > 1:
                    raise NotImplementedError(
                        (
                            f"Cannot have multiple dates in {self} "
                            "when using hindcast {date=}, {hdate=}"
                        )
                    )
                date = hdate
                del hdate

            if len(step) > 1 and len(time) > 1:
                raise NotImplementedError(
                    f"Cannot have multiple steps and multiple times in {self}"
                )

            datetimes = set()
            for d, t, s in itertools.product(date, time, step):
                new = build_datetime(date=d, time=t, step=s)
                if new in datetimes:
                    raise DuplicateDateTimeError(
                        f"Duplicate datetime '{new}' when processing << {self} >> already in {datetimes}"
                    )
                datetimes.add(new)
            return sorted(list(datetimes))

        raise ValueError(f"{name=} Cannot count number of elements in {self}")

    def do_load(self, others={}):
        if not self._do_load:
            from climetlab import load_dataset, load_source

            func = {
                None: load_source,
                "load_source": load_source,
                "load_dataset": load_dataset,
            }[self.function]

            ds = func(**self.kwargs)

            print(f"  Loading {self.name} of len {len(ds)}: {ds}")
            self._do_load = ds
        return self._do_load

    def get_first_field(self):
        return self.do_load()[0]

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

        self._inheritance_others = others
        self._inheritance_done = True

    def __repr__(self) -> str:
        def repr(v):
            if isinstance(v, list):
                return f"{'/'.join(str(x) for x in v)}"
            return str(v)

        details = ", ".join(f"{k}={repr(v)}" for k, v in self.kwargs.items())
        return f"Input({self.name}, {details})<{self.inherit}"

    def substitute(self, *args, **kwargs):
        new_kwargs = substitute(self.kwargs.copy(), *args, **kwargs)
        i = Input(
            {
                self.name: dict(
                    kwargs=new_kwargs,
                    inherit=self.inherit,
                    function=self.function,
                )
            }
        )
        # if self._inheritance_others:
        #    i.process_inheritance(self._inheritance_others)
        return i


def make_list_int(value):
    if isinstance(value, str):
        if "/" not in value:
            return [value]
        bits = value.split("/")
        if len(bits) == 3 and bits[1].lower() == "to":
            value = list(range(int(bits[0]), int(bits[2]) + 1, 1))

        elif len(bits) == 5 and bits[1].lower() == "to" and bits[3].lower() == "by":
            value = list(range(int(bits[0]), int(bits[2]) + int(bits[4]), int(bits[4])))

    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return value

    raise ValueError(f"Cannot make list from {value}")


def build_datetime(date, time, step):
    if isinstance(date, str):
        from climetlab.utils.dates import to_datetime

        date = to_datetime(date)

    if isinstance(time, int):
        if time < 24:
            time = f"{time:02d}00"
        else:
            time = f"{time:04d}"

    assert isinstance(date, datetime.datetime), date
    assert date.hour == 0 and date.minute == 0 and date.second == 0, date

    assert isinstance(time, str), time
    assert len(time) == 4, time
    assert int(time) >= 0 and int(time) < 2400, time
    if 0 < int(time) < 100:
        print(f"WARNING: {time=}, using time with minutes is unusual.")

    dt = datetime.datetime(
        year=date.year,
        month=date.month,
        day=date.day,
        hour=int(time[0:2]),
        minute=int(time[2:4]),
    )

    if step:
        dt += datetime.timedelta(hours=step)

    return dt


class InputHandler:
    def __init__(self, args, input, output):
        inputs = Inputs(input)
        self.output = output
        self.loops = [
            c
            if isinstance(c, Loop) and c.inputs == inputs
            else Loop(c, inputs, parent=self)
            for c in args
        ]
        if not self.loops:
            raise NotImplementedError("No loop")

    def iter_cubes(self):
        for loop in self.loops:
            yield from loop.iterate()

    @property
    def first_cube(self):
        return self.first_cube_creator.to_cube()

    @property
    def first_cube_creator(self):
        for loop in self.loops:
            for cube_creator in loop.iterate():
                return cube_creator

    @property
    def chunking(self):
        return self.first_cube.chunking(self.output.chunking)

    @cached_property
    def n_cubes(self):
        n = 0
        for loop in self.loops:
            for i in loop.iterate():
                n += 1
        return n

    @cached_property
    def _info(self):
        infos = [loop._info for loop in self.loops]

        # check all are the same
        ref = infos[0]
        for c in infos:
            assert (np.array(ref.grid_points) == np.array(c.grid_points)).all(), (
                "grid_points mismatch",
                c.grid_points,
                ref.grid_points,
                type(ref.grid_points),
            )
            assert ref.resolution == c.resolution, (
                "resolution mismatch",
                c.resolution,
                ref.resolution,
            )
            assert ref.variables == c.variables, (
                "variables mismatch",
                c.variables,
                ref.variables,
            )

        coords = deepcopy(ref.coords)
        assert (
            "valid_datetime" in coords
        ), f"valid_datetime not found in coords {coords}"
        coords["valid_datetime"] = self.get_datetimes()

        for info in infos:
            for name, values in info.coords.items():
                if name == "valid_datetime":
                    continue
                assert values == ref.coords[name], (values, ref.coords[name])

        return Info(
            ref.first_field,
            ref.grid_points,
            ref.resolution,
            coords,
            ref.variables,
        )

    @property
    def first_field(self):
        return self._info.first_field

    @property
    def grid_points(self):
        return self._info.grid_points

    @property
    def resolution(self):
        return self._info.resolution

    @property
    def coords(self):
        return self._info.coords

    @property
    def variables(self):
        return self._info.variables

    @property
    def shape(self):
        return [len(c) for c in self.coords.values()] + list(self.first_field.shape)

    def get_datetimes(self):
        # merge datetimes from all loops and check there are no duplicates
        datetimes = set()
        for i in self.loops:
            assert isinstance(i, Loop), i
            new = i.get_datetimes()
            for d in new:
                assert d not in datetimes, (d, datetimes)
                datetimes.add(d)
        datetimes = sorted(list(datetimes))

        def check(datetimes):
            if not datetimes:
                raise ValueError("No datetimes found.")
            if len(datetimes) == 1:
                raise ValueError("Only one datetime found.")

            delta = None
            for i in range(1, len(datetimes)):
                new = (datetimes[i] - datetimes[i - 1]).total_seconds() / 3600
                if not delta:
                    delta = new
                    continue
                if new != delta:
                    raise ValueError(
                        f"Datetimes are not regularly spaced: "
                        f"delta={new} hours  (date {i-1}={datetimes[i-1]}  date {i}={datetimes[i]}) "
                        f"Expecting {delta} hours  (date {0}={datetimes[0]}  date {1}={datetimes[1]}) "
                    )

        check(datetimes)

        return datetimes

    @property
    def frequency(self):
        datetimes = self.get_datetimes()
        freq = (datetimes[1] - datetimes[0]).total_seconds() / 3600
        assert round(freq) == freq, freq
        assert int(freq) == freq, freq
        return int(freq)

    def __repr__(self):
        return "InputHandler\n  " + "\n  ".join(str(i) for i in self.loops)


class Loop(dict):
    def __init__(self, dic, inputs, parent=None):
        assert isinstance(dic, dict), dic
        assert len(dic) == 1, dic
        super().__init__(dic)

        self.parent = parent
        self.name = list(dic.keys())[0]
        self.config = deepcopy(dic[self.name])

        assert "applies_to" in self.config, self.config
        applies_to = self.config.pop("applies_to")
        self.applies_to_inputs = Inputs(
            [input for input in inputs if input.name in applies_to]
        )
        for i in self.applies_to_inputs:
            i.process_inheritance(inputs)

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
            yield CubeCreator(
                inputs=self.applies_to_inputs,
                vars=dict(zip(self.values.keys(), items)),
                loop_config=self.config,
                output=self.parent.output,
            )

    @property
    def first(self):
        return CubeCreator(
            inputs=self.applies_to_inputs,
            vars={k: lst[0] for k, lst in self.values.items() if lst},
            loop_config=self.config,
            output=self.parent.output,
        )

    @cached_property
    def _info(self):
        first_info = self.first._info
        coords = deepcopy(first_info.coords)
        assert (
            "valid_datetime" in coords
        ), f"valid_datetime not found in coords {coords}"
        coords["valid_datetime"] = self.get_datetimes()
        return Info(
            first_field=first_info.first_field,
            grid_points=first_info.grid_points,
            resolution=first_info.resolution,
            coords=coords,
            variables=first_info.variables,
        )

    def get_datetimes(self):
        # merge datetimes from all cubecreators and check there are no duplicates
        datetimes = set()

        for i in self.iterate():
            assert isinstance(i, CubeCreator), i
            new = i.get_datetimes()

            duplicates = datetimes.intersection(set(new))
            if duplicates:
                raise DuplicateDateTimeError(
                    f"{len(duplicates)} duplicated datetimes "
                    f"'{sorted(list(duplicates))[0]},...' when processing << {self} >>"
                )

            datetimes = datetimes.union(set(new))
        return sorted(list(datetimes))


class DuplicateDateTimeError(ValueError):
    pass


class CubeCreator:
    def __init__(self, inputs, vars, loop_config, output):
        self._loop_config = loop_config
        self._vars = vars
        self._inputs = inputs
        self.output = output

        self.inputs = inputs.substitute(vars=vars, ignore_missing=True)

    @property
    def length(self):
        return 1

    def __repr__(self) -> str:
        out = f"CubeCreator ({self.length}):\n"
        out += f" loop_config: {self._loop_config}"
        out += f" vars: {self._vars}\n"
        out += " Inputs:\n"
        for _i, i in zip(self._inputs, self.inputs):
            out += f"- {_i}\n"
            out += f"  {i}\n"
        return out

    def do_load(self):
        return self.inputs.do_load()

    def get_datetimes(self):
        return self.inputs.get_datetimes()

    def to_cube(self):
        cube, data = self._to_data_and_cube()
        return cube

    def _to_data_and_cube(self):
        data = self.do_load()

        start = time.time()
        print("Sorting dataset", self.output.order_by, self.output.remapping)
        cube = data.cube(
            self.output.order_by,
            remapping=self.output.remapping,
            flatten_values=self.output.flatten_values,
        )
        cube = cube.squeeze()

        def check():
            actual_dic = cube.user_coords
            requested_dic = self.output.order_by
            assert self.output.statistics in actual_dic

            for key in set(list(actual_dic.keys()) + list(requested_dic.keys())):
                actual = actual_dic[key]
                requested = requested_dic[key]

                actual = list(actual)

                if requested == "ascending":
                    assert actual == sorted(
                        actual
                    ), f"Requested= {requested} Actual= {actual}"
                    continue
                assert actual == requested, f"Requested= {requested} Actual= {actual}"

        check()

        print(f"Sorting done in {seconds(time.time()-start)}.")

        return cube, data

    @property
    def _info(self):
        cube, data = self._to_data_and_cube()

        first_field = data[0]
        grid_points = first_field.grid_points()
        resolution = first_field.resolution
        coords = cube.user_coords
        variables = list(coords[list(coords.keys())[1]])

        return Info(first_field, grid_points, resolution, coords, variables)


def _format_list(x):
    if isinstance(x, (list, tuple)):
        if isinstance(x[0], datetime.datetime):
            is_regular = True
            delta = x[1] - x[0]
            for prev, current in zip(x[:-1], x[1:]):
                if current - prev != delta:
                    is_regular = False
                    break
            if is_regular:
                return f"{_format_list(x[0])}/to/{_format_list(x[-1])}/by/{delta.total_seconds()/3600}"

        return "/".join(_format_list(_) for _ in x)

    if isinstance(x, datetime.datetime):
        return x.strftime("%Y%m%d.%H%M")
    return str(x)


class Info:
    def __init__(self, first_field, grid_points, resolution, coords, variables):
        assert len(set(variables)) == len(variables), (
            "Duplicate variables",
            variables,
        )

        assert grid_points[0].shape == grid_points[1].shape, (
            grid_points[0].shape,
            grid_points[1].shape,
            grid_points[0],
            grid_points[1],
        )

        assert len(grid_points) == 2, grid_points

        expected = math.prod(first_field.shape)
        assert len(grid_points[0]) == expected, (len(grid_points[0]), expected)

        self.first_field = first_field
        self.grid_points = grid_points
        self.resolution = resolution
        self.coords = coords
        self.variables = variables

    def __repr__(self):
        shape = (
            f"{','.join([str(len(v)) for k, v in self.coords.items()])},"
            + f"{','.join([str(_) for _ in self.first_field.shape])}"
        )
        shape = shape.rjust(20)
        return (
            f"Info(first_field={self.first_field}, "
            f"resolution={self.resolution}, "
            f"variables={'/'.join(self.variables)})"
            f"coords={', '.join([k + ':' + _format_list(v) for k, v in self.coords.items()])}"
            f" {shape}"
        )


class LoadersConfig(Config):
    def __init__(self, config, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        if "description" not in self:
            raise ValueError("Must provide a description in the config.")

        if not isinstance(self.input, (tuple, list)):
            print(f"WARNING: {self.input=} is not a list")
            self.input = [self.input]

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

    def input_handler(self):
        return InputHandler(self.loops, self.input, output=self.output)

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
        from climetlab.utils.dates import to_datetime

        self.start = to_datetime(self._config.get("start"))
        self.stop = to_datetime(self._config.get("stop"))
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
