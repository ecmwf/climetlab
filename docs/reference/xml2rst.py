#!/usr/bin/env python3
# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import sys
import xmltodict
import yaml
from collections import defaultdict, OrderedDict
import argparse

yaml.Dumper.ignore_aliases = lambda *args: True

DEFS = OrderedDict()

T = {
    "on": True,
    "off": False,
    "no": False,
    "stringarray()": [],
    "intarray()": [],
    "floatarray()": [],
}

TYPES = {
    "string": "str",
    "bool": "bool",
    "Colour": "str",
    "NoBoundaries": "bool",
    "NoCities": "bool",
    "LineStyle": "str",
    "int": "int",
    "NoCoastPlotting": "bool",
    "NoGridPlotting": "bool",
    "NoLabelPlotting": "bool",
    "float": "float",
    "LevelSelection": "str",
    "floatarray": "List[float]",
    "ColourTechnique": "str",
    "stringarray": "List[str]",
    "ListPolicy": "str",
    "intarray": "List[int]",
    "HeightTechnique": "str",
    "NoOutLayerTechnique": "bool",
    "SymbolMode": "str",
}


def tidy(x):

    if isinstance(x, (list, tuple)):
        return [tidy(y) for y in x]

    if isinstance(x, (dict, OrderedDict)):
        d = OrderedDict()
        for k, v in x.items():
            d[tidy(k)] = tidy(v)

        return d

    if isinstance(x, str):
        if x.startswith("@"):
            return x[1:]

    try:
        return int(x)
    except Exception:
        pass

    try:
        return float(x)
    except Exception:
        pass

    # x = T.get(x, x)

    # if isinstance(x, str):

    return T.get(x, x)


def cleanup(p):
    p = str(p)
    p = p.strip().replace("\n", " ").replace("\t", " ")
    n = len(p)
    while True:
        p = p.replace("  ", " ")
        if len(p) == n:
            break
        n = len(p)
    return p


class Param:
    def __init__(self, defs):
        self._defs = defs

    @property
    def name(self):
        return self._defs.get("name")

    @property
    def documentation(self):
        return cleanup(self._defs.get("documentation", ""))

    @property
    def default(self):

        default = self._defs.get("default")
        if default in (None, False, True):
            return default

        try:
            return float(default)
        except Exception:
            pass

        try:
            return float(default)
        except Exception:
            pass

        return repr(default).replace("'", '"')

    @property
    def values(self):

        f = self._defs.get("from")
        t = self._defs.get("to")

        if t == "bool":
            return t

        if "values" in self._defs:
            return ", ".join(
                [repr(tidy(x)) for x in self._defs.get("values").split("/")]
            )

        if f == t:
            return t

        return "%s(%s)" % (t, f)

    @property
    def python_type(self):
        t = self._defs.get("to")
        return TYPES[t]


class Klass:
    def __init__(self, defs):

        self._defs = defs
        self._inherits = None
        self._parameters = None
        self._super = False

    @property
    def name(self):
        return self._defs.get("name")

    @property
    def documentation(self):
        return cleanup(self._defs.get("documentation", ""))

    @property
    def action(self):
        action = self._defs.get("python")
        if action is None:
            for parent in self.inherits:
                if parent.action:
                    assert action is None or action == parent.action, (
                        action,
                        parent.action,
                    )
                    action = parent.action

        if action is None or action[0] == action[0].upper():
            return None

        return action

    @property
    def parameters(self):
        if self._parameters is None:
            self._parameters = []
            for parent in self.inherits:
                self._parameters.extend(parent.parameters)

            parms = self._defs.get("parameter", [])
            if not isinstance(parms, list):
                parms = [parms]

            for p in parms:
                if p.get("python", True):
                    self._parameters.append(Param(p))
        return self._parameters

    @property
    def inherits(self):
        if self._inherits is None:
            self._inherits = []
            if self._defs.get("inherits"):
                for p in self._defs.get("inherits").split("/"):
                    try:
                        self._inherits.append(DEFS[p])
                        DEFS[p]._super = True
                    except KeyError:
                        print(
                            "Cannot find super class '%s' for '%s'" % (p, self.name),
                            file=sys.stderr,
                        )
        return self._inherits


def load(n):
    with open(n) as f:
        x = tidy(xmltodict.parse(f.read()))

    klass = x["magics"]["class"]
    klass["PATH"] = n

    assert klass["name"] not in DEFS, (klass["name"], n, DEFS[klass["name"]])
    DEFS[klass["name"]] = Klass(klass)


# TODO: Use Jinga templates


def produce_rst():
    print("Plotting")
    print("========")
    print()

    for action, klasses in sorted(ACTIONS.items()):
        print()
        print(action)
        print("-" * len(action))
        print()
        documentation = []
        print(".. %s" % [k.name for k in klasses])
        print()
        for k in klasses:
            documentation.append(k.documentation)
        print(cleanup(" ".join(documentation)))
        print()

        print(".. list-table::")
        print("   :header-rows: 1")
        print("   :widths: 70 20 10")
        print()
        print("   * - | Name")
        print("     - | Type")
        print("     - | Default")

        for k in klasses:

            for p in k.parameters:
                print("   * - |", "**%s**" % p.name)
                print("       |", p.documentation)
                print("     - |", p.values)
                print("     - |", p.default)
                # print("     -", p.documentation)
        print()


def produce_python():

    print(
        "\n".join(
            [
                "import inspect",
                "from typing import List",
                "from Magics import macro",
                "",
                "",
                """def _given_args(frame):
    func = frame.f_globals[frame.f_code.co_name]
    user_args = inspect.getargvalues(frame)
    code_args = inspect.getfullargspec(func)
    given = {}

    if code_args.kwonlydefaults:
        pairs = list(code_args.kwonlydefaults.items())
    else:
        pairs = list(zip(code_args.args, code_args.defaults))

    for name, value in pairs:
        if user_args.locals[name] is not value:
            given[name] = user_args.locals[name]
    return given""",
            ]
        )
    )

    for action, klasses in sorted(ACTIONS.items()):
        print()
        print()
        print("def %s(" % action)
        print("    *,")

        # documentation = []
        # print(".. %s" % [k.name for k in klasses])
        # print()
        # for k in klasses:
        #     documentation.append(k.documentation)
        # print(cleanup(" ".join(documentation)))
        # print()

        seen = set()

        for k in klasses:
            print("    # [%s]" % (k.name,), k.documentation)
            for p in k.parameters:

                c = "#" if p.name in seen else ""

                print("   ", "%s%s: %s = %s," % (c, p.name, p.python_type, p.default))
                seen.add(p.name)
                # print("       |", p.documentation)
                # print("     - |", p.values)
                # print("     - |", p.default)
                # print("     -", p.documentation)
        print("):")
        print("    return macro.%s(**_given_args(inspect.currentframe()))" % (action,))


def produce_yaml():

    print("---")

    for action, klasses in sorted(ACTIONS.items()):
        print()

        print("%s:" % (action,))

        for k in klasses:
            for p in k.parameters:
                print("  -", p.name)


parser = argparse.ArgumentParser()
parser.add_argument("--rst", action="store_true")
parser.add_argument("--python", action="store_true")
parser.add_argument("--yaml", action="store_true")
parser.add_argument(
    "xml", metavar="N", nargs="+",
)
args = parser.parse_args()


for n in args.xml:
    load(n)

for v in DEFS.values():
    v.inherits

ACTIONS = defaultdict(list)
for k, v in DEFS.items():
    if not v._super:
        if v.action is not None:
            ACTIONS[v.action].append(v)


if args.rst:
    produce_rst()

if args.python:
    produce_python()

if args.yaml:
    produce_yaml()
