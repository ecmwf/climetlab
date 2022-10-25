# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import inspect
import json
import re

import requests
import yaml

try:
    # There is a bug in tqdm that expects ipywidgets
    # to be installed if running in a notebook
    import ipywidgets  # noqa F401
    from tqdm.auto import tqdm  # noqa F401
except ImportError:
    from tqdm import tqdm  # noqa F401


def download_and_cache(url, return_none_on_404=False, **kwargs):
    from climetlab.sources.url import download_and_cache

    try:
        return download_and_cache(url, **kwargs)
    except requests.HTTPError as e:
        if return_none_on_404:
            if e.response is not None and e.response.status_code == 404:
                return None
        raise


def get_json(url: str, cache=False):
    if cache:
        with open(download_and_cache(url)) as f:
            return json.loads(f.read())

    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def _dummy(**kwargs):
    pass


def consume_args(func1, func2, *args, **kwargs):

    # print("=====>", args, kwargs)

    if func1 is None:
        func1 = _dummy

    if func2 is None:
        func2 = _dummy

    args1 = set()
    sig1 = inspect.signature(func1)
    for name, param in sig1.parameters.items():
        if param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            args1.add(name)

    # print(f"{func1.__name__}{sig1}")

    args2 = set()
    sig2 = inspect.signature(func2)
    for name, param in sig2.parameters.items():
        if param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            args2.add(name)

    # print(f"{func2.__name__}{sig2}")

    common = args1.intersection(args2)
    common.discard("self")

    if common:
        raise NotImplementedError(
            f"{func1.__name__}{sig1} and {func2.__name__}{sig2} cannot share the same parameter(s): {common}"
        )

    spec = inspect.getfullargspec(func1)

    args_1 = []
    kwargs_1 = {}

    args = list(args)

    spec_args = [a for a in spec.args if a != "self"]

    for a in spec_args:
        if a in kwargs:
            break
        if not args:
            break
        args_1.append(args.pop(0))

    n = len(args_1)
    for a in spec_args[n:] + spec.kwonlyargs:
        if a in kwargs:
            kwargs_1[a] = kwargs.pop(a)

    # print('<=====', args_1, kwargs_1, args, kwargs)
    return args_1, kwargs_1, args, kwargs


def string_to_args(s):
    def typed(x):
        try:
            return int(x)
        except ValueError:
            pass

        try:
            return float(x)
        except ValueError:
            pass

        return x

    assert isinstance(s, str), s
    m = re.match(r"([\w\-]+)(\((.*)\))?", s)
    if not m:
        raise ValueError(f"Invalid argument '{s}'")

    name = m.group(1)

    if m.group(2) is None:
        return name, [], {}

    args = []
    kwargs = {}
    bits = [x.strip() for x in m.group(3).split(",") if x.strip()]
    for bit in bits:
        if "=" in bit:
            k, v = bit.split("=")
            kwargs[k.strip()] = typed(v.strip())
        else:
            args.append(typed(bit))

    return name, args, kwargs


def load_json_or_yaml(path):
    with open(path, "r") as f:
        if path.endswith(".json"):
            return json.load(f)
        if path.endswith(".yaml") or path.endswith(".yml"):
            return yaml.safe_load(f)
        raise ValueError(
            f"Cannot read file {path}. Need json or yaml with appropriate extension."
        )


def progress_bar(*, total=None, iterable=None, initial=0, desc=None):
    return tqdm(
        iterable=iterable,
        total=total,
        initial=initial,
        unit_scale=True,
        unit_divisor=1024,
        unit="B",
        disable=False,
        leave=False,
        desc=desc,
        # dynamic_ncols=True, # make this the default?
    )
