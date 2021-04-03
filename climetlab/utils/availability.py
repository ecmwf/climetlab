import functools
import inspect
import json
import os

from climetlab.utils.factorise import factorise


class Availability:
    def __init__(self, avail):
        if isinstance(avail, str):
            with open(avail) as f:
                avail = json.loads(f.read())
        self._avail = factorise(avail)

    def _repr_html_(self):
        return self._avail._repr_html_()


def availability(avail):

    if isinstance(avail, str):
        if not os.path.isabs(avail):
            caller = os.path.dirname(inspect.stack()[1].filename)
            avail = os.path.join(caller, avail)

    avail = Availability(avail)

    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        return inner

    return outer
