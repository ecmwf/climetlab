import functools
import inspect
import json
import os

from climetlab.utils.factorise import Tree, factorise


class Availability:
    def __init__(self, avail):
        if not isinstance(avail, Tree):
            if isinstance(avail, str):
                with open(avail) as f:
                    avail = json.loads(f.read())
            avail = factorise(avail)
        self._tree = avail

    def _repr_html_(self):
        return self._tree._repr_html_()

    def select(self, *args, **kwargs):
        return self._tree.select(*args, **kwargs)


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
