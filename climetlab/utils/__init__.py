# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import inspect


def download_and_cache(url: str) -> str:
    """[summary]

    :param url: [description]
    :type url: str
    :return: [description]
    :rtype: str
    """
    from climetlab import load_source

    return load_source("url", url).path


def bytes_to_string(n):
    u = ["", " KiB", " MiB", " GiB", " TiB", " PiB"]
    i = 0
    while n >= 1024:
        n /= 1024.0
        i += 1
    return "%g%s" % (int(n * 10 + 0.5) / 10.0, u[i])


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
