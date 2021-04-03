import functools
import inspect
import json
import os

from climetlab.utils.factorise import factorise


class Availability:
    def __init__(self, avail):
        self._avail = factorise(avail)

    def __repr__(self):
        return repr(self._avail.to_list())


def availability(avail):

    if isinstance(avail, str):
        if not os.path.isabs(avail):
            caller = os.path.dirname(inspect.stack()[1].filename)
            avail = os.path.join(caller, avail)

        with open(avail) as f:
            avail = json.loads(f.read())

    avail = Availability(avail)

    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        return inner

    return outer
