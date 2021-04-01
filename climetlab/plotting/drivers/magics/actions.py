# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# Keep linters happy
# N801 = classes should start with uppercase
# N806 = variables should be lower case

import logging
import warnings

from .convertions import convert


class NoMagics:
    def plot(self, *args, **kwargs):
        raise NotImplementedError(
            "Magics was not loaded successfully, plotting is not supported."
        )


try:
    import Magics
    from Magics import macro

    try:
        Magics.strict_mode()
    except Exception as e:
        warnings.warn(e)
except Exception as e:
    warnings.warn(e)
    macro = NoMagics()


LOG = logging.getLogger(__name__)


class Action:

    default_style: object = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __repr__(self):
        x = ["macro.%s(" % (self.action,)]
        for k, v in sorted(self.kwargs.items()):
            x.append("\n   %s=%r," % (k, v))
        x.append("\n    )")
        return "".join(x)

    def to_yaml(self):
        return {self.action: self.kwargs}

    @property
    def action(self):
        return self.__class__.__name__

    def execute(self):
        return getattr(macro, self.action)(
            **convert(self.action, self.kwargs)
        ).execute()

    def update(self, action, values):
        if not isinstance(self, action):
            return None
        for k, v in values.items():
            if k[0] in ("+",):
                self.kwargs[k[1:]] = v
            if k[0] in ("-",):
                self.kwargs.pop(k[1:], None)
            if k[0] in ("=",) and k[1:] not in self.kwargs:
                self.kwargs[k[1:]] = v
        return self


class mcont(Action):  # noqa: N801
    pass


class mcoast(Action):  # noqa: N801
    pass


class mmap(Action):  # noqa: N801
    def page_ratio(self):
        # TODO: Use projection
        south = self.kwargs.get("subpage_lower_left_latitude", -90.0)
        west = self.kwargs.get("subpage_lower_left_longitude", -180)
        north = self.kwargs.get("subpage_upper_right_latitude", 90.0)
        east = self.kwargs.get("subpage_upper_right_longitude", 180.0)
        return (north - south) / (east - west)


class FieldAction(Action):
    default_style = mcont(contour_automatic_setting="climetlab", legend=False)


class mgrib(FieldAction):  # noqa: N801
    pass


class mnetcdf(FieldAction):  # noqa: N801
    pass


class minput(FieldAction):  # noqa: N801
    pass


class mtable(Action):  # noqa: N801
    pass


class mtext(Action):  # noqa: N801
    pass


class msymb(Action):  # noqa: N801
    pass


class output(Action):  # noqa: N801
    pass


def plot(*args, **kwargs):
    return macro.plot(*args, **kwargs)


def lookup(name):
    return globals()[name]
