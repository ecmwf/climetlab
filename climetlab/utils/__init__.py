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


def consume_args(func, *args, **kwargs):
    spec = inspect.getfullargspec(func)

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

    # print(args_1, kwargs_1, args, kwargs)
    return args_1, kwargs_1, args, kwargs
