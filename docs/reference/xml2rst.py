#!/usr/bin/env python3
# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import argparse
import json
import os
import re
import sys
from collections import OrderedDict, defaultdict
from textwrap import fill

import xmltodict
import yaml

yaml.Dumper.ignore_aliases = lambda *args: True

DEFS = OrderedDict()
ENUMS = {}

T = {
    "on": True,
    "off": False,
    "no": False,
    "-INT_MAX": -2147483647,
    "INT_MAX": 2147483647,
    "metview": False,  # Visible=metview => false
}


def _snake_case(m):
    return m.group(1).lower() + "-" + m.group(2).lower()


def to_snake_case(k):
    return re.sub(r"(.+?)([A-Z])", _snake_case, k, 0).lower()


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


################################################################


class String:

    values = None
    python_type = "str"
    yaml_type = "String"
    json_schema = {"type": "string"}

    def __init__(self, param):
        self._param = param
        self.yaml_default = param._defs.get("default")
        self.python_default = self.yaml_default


class Bool:

    values = None
    python_type = "bool"
    yaml_type = "Bool"
    json_schema = {"type": "boolean"}

    def __init__(self, param):
        self._param = param
        self.yaml_default = param._defs.get("default")
        self.python_default = self.yaml_default


class Int:

    values = None
    python_type = "int"
    yaml_type = "Int"
    json_schema = {"type": "integer"}

    def __init__(self, param):
        self._param = param
        self.yaml_default = param._defs.get("default")
        if self.yaml_default is not None:
            self.yaml_default = int(self.yaml_default)
        self.python_default = self.yaml_default


class Float:

    values = None
    python_type = "float"
    yaml_type = "Float"

    json_schema = {"type": "number"}

    def __init__(self, param):
        self._param = param
        self.yaml_default = param._defs.get("default")
        if self.yaml_default is not None:
            self.yaml_default = float(self.yaml_default)
        self.python_default = self.yaml_default


class Latitude(Float):
    json_schema = {"$ref": "definitions.json#/definitions/latitude"}


class Longitude(Float):
    json_schema = {"$ref": "definitions.json#/definitions/longitude"}


class IntList:

    values = None
    python_type = "List[int]"
    yaml_type = "IntList"
    json_schema = {"type": "array", "items": {"type": "integer"}}

    def __init__(self, param):
        self._param = param
        assert param._defs.get("default") == "intarray()", param._defs.get("default")
        self.yaml_default = []
        self.python_default = self.yaml_default


class FloatList:

    values = None
    python_type = "List[float]"
    yaml_type = "FloatList"
    json_schema = {"type": "array", "items": {"type": "number"}}

    def __init__(self, param):
        self._param = param
        assert param._defs.get("default") == "floatarray()", param._defs.get("default")
        self.yaml_default = []
        self.python_default = self.yaml_default


class StringList:

    values = None
    python_type = "List[str]"
    yaml_type = "StringList"
    json_schema = {"type": "array", "items": {"type": "string"}}

    def __init__(self, param):
        self._param = param
        assert param._defs.get("default") == "stringarray()", param._defs.get("default")
        self.yaml_default = []
        self.python_default = self.yaml_default


class ColourList:

    values = None
    python_type = "List[str]"
    yaml_type = "ColourList"
    json_schema = {
        "type": "array",
        "items": {"$ref": "definitions.json#/definitions/colour"},
    }

    def __init__(self, param):
        self._param = param
        assert param._defs.get("default") == "stringarray()", param._defs.get("default")
        self.yaml_default = []
        self.python_default = self.yaml_default


class Colour:

    values = None
    python_type = "str"
    yaml_type = "Colour"
    json_schema = {"$ref": "definitions.json#/definitions/colour"}

    def __init__(self, param):
        self._param = param
        self.yaml_default = param._defs.get("default")
        self.python_default = self.yaml_default


class Enum:

    python_type = "str"
    yaml_type = "string"

    def __init__(self, param):
        self._param = param

        if param._defs.get("to") in ENUMS:
            self.values = ENUMS[param._defs.get("to")]["values"].keys()

        if "values" in param._defs:
            self.values = param._defs.get("values").split("/")

        if self._param._defs.get("option"):
            self.values = []
            for o in self._param._defs.get("option"):
                self.values.append(o["fortran"])

        self.values = [tidy(x) for x in self.values]

        self.yaml_default = param._defs.get("default")
        self.python_default = self.yaml_default

    @property
    def json_schema(self):
        def _(x):
            if x == 0:
                return False
            if x == 1:
                return True
            return x

        if False in self.values or True in self.values:
            if "style_name" in self.values:
                return {"type": ["string", "boolean"]}
            return {"type": ["string", "boolean"], "enum": [_(x) for x in self.values]}

        if self._param._defs.get("to") in ENUMS:
            return {
                "$ref": "definitions.json#/definitions/{}".format(
                    to_snake_case(self._param._defs.get("to"))
                )
            }

        return {"type": "string", "enum": sorted(self.values)}


################################################################


class Param:
    def __init__(self, defs):
        self._defs = defs
        self._type = None
        if self.type.values == [False, True] or self.type.values == [True, False]:
            self._type = Bool(self)

    @property
    def name(self):
        return self._defs.get("name")

    @property
    def documentation(self):
        return cleanup(self._defs.get("documentation", ""))

    @property
    def python_default(self):
        return repr(self.type.python_default).replace("'", '"')

    @property
    def yaml_default(self):
        return self.type.yaml_default

    @property
    def type(self):
        if self._type is None:
            t = self._defs.get("to")
            if t.startswith("No"):
                t = "Bool"

            if "colour" in self.name and t == "stringarray":
                t = "ColourList"

            t = t.replace("array", "List")

            t = t[0].upper() + t[1:]

            if "values" in self._defs or t in ENUMS:
                t = "Enum"

            if self._defs.get("option"):
                t = "Enum"

            if "latitude" in self.name and t != "String":
                t = "Latitude"

            if "longitude" in self.name and t != "String":
                t = "Longitude"

            if t not in globals():
                print(t, self.name, file=sys.stderr)

            self._type = globals().get(t, String)(self)

        return self._type

    @property
    def python_values(self):

        values = self.type.values
        if values is not None:
            return ", ".join([repr(x).replace("'", '"') for x in values])

        return self.python_type

    @property
    def yaml_values(self):
        return self.type.values

    @property
    def yaml_type(self):
        return self.type.yaml_type

    @property
    def python_type(self):
        return self.type.python_type

    @property
    def json_schema(self):
        return self.type.json_schema


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
    def rank(self):
        return int(self._defs.get("python_rank", 100000))

    def __lt__(self, other):
        return self.rank < other.rank

    @property
    def documentation(self):
        return cleanup(self._defs.get("userdoc", ""))

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
                if p.get("python", True) and p.get("visible", True):
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
        try:
            x = tidy(xmltodict.parse(f.read()))
        except Exception as e:
            raise Exception(n, e)

    klass = x["magics"]["class"]
    klass["PATH"] = n

    assert klass["name"] not in DEFS, (klass["name"], n, DEFS[klass["name"]])
    DEFS[klass["name"]] = Klass(klass)


# TODO: Use Jinga templates


def produce_rst():
    print(
        ".. DO NOT EDIT - This page is automatically generated by %s"
        % (os.path.basename(sys.argv[0]),)
    )
    print()
    print("Plotting")
    print("========")
    print()

    for action, klasses in sorted(ACTIONS.items()):
        print()
        print(".. _magics-{}:".format(action))

        print()
        print(action)
        print("-" * len(action))
        print()
        documentation = []
        print(".. %s" % [k.name for k in sorted(klasses)])
        print()
        for k in sorted(klasses):
            documentation.append(k.documentation)
        print(fill(cleanup(" ".join(documentation))))
        print()

        print(".. list-table::")
        print("   :header-rows: 1")
        print("   :widths: 70 20 10")
        print()
        print("   * - | Name")
        print("     - | Type")
        print("     - | Default")
        print()

        seen = set()

        for k in sorted(klasses):

            for p in k.parameters:

                if p.name in seen:
                    continue

                seen.add(p.name)

                print("   * - |", "**%s**" % p.name)
                print("       |", fill(p.documentation, subsequent_indent=" " * 9))
                print("     - |", p.python_values)
                print("     - |", p.python_default)
                print()
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

        seen = set()

        for k in sorted(klasses):
            print("    # [%s]" % (k.name,), k.documentation)
            for p in k.parameters:

                c = "#" if p.name in seen else ""

                print(
                    "   ",
                    "%s%s: %s = %s," % (c, p.name, p.python_type, p.python_default),
                )
                seen.add(p.name)
                # print("       |", p.documentation)
                # print("     - |", p.values)
                # print("     - |", p.default)
                # print("     -", p.documentation)
        print("):")
        print("    return macro.%s(**_given_args(inspect.currentframe()))" % (action,))


def produce_yaml():

    m = {}

    for action, klasses in sorted(ACTIONS.items()):

        m[action] = []

        for k in sorted(klasses):
            for p in k.parameters:
                d = dict(name=p.name, type=p.yaml_type)
                if p.yaml_default:
                    d["default"] = p.yaml_default

                if p.yaml_values:
                    d["values"] = p.yaml_values
                m[action].append(d)

    print(yaml.dump(m, default_flow_style=False))


def produce_schemas(directory):

    path = os.path.join(directory, "definitions.json")
    with open(path) as f:
        definitions = json.load(f)["definitions"]

    for k, v in ENUMS.items():
        name = to_snake_case(k)
        definitions[name] = {"type": "string", "enum": sorted(v["values"].keys())}

    with open(path + ".tmp", "w") as f:
        print(
            json.dumps({"definitions": definitions}, sort_keys=True, indent=4), file=f
        )
    os.rename(path + ".tmp", path)

    for action, klasses in sorted(ACTIONS.items()):

        properties = {}

        for k in sorted(klasses):
            for p in k.parameters:
                properties[p.name] = p.json_schema

        schema = {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }

        path = os.path.join(directory, "{}.json".format(action))
        with open(path + ".tmp", "w") as f:
            print(json.dumps(schema, sort_keys=True, indent=4), file=f)
        os.rename(path + ".tmp", path)


parser = argparse.ArgumentParser()
parser.add_argument("--rst", action="store_true")
parser.add_argument("--python", action="store_true")
parser.add_argument("--yaml", action="store_true")
parser.add_argument("--types")
parser.add_argument("--schemas")
parser.add_argument(
    "xml",
    metavar="N",
    nargs="+",
)
args = parser.parse_args()

if args.types:
    with open(args.types) as f:
        ENUMS = yaml.load(f, Loader=yaml.SafeLoader)

for n in args.xml:
    load(n)

assert DEFS

for v in DEFS.values():
    v.inherits

ACTIONS = defaultdict(list)
for k, v in DEFS.items():
    if not v._super and v.action is not None:
        ACTIONS[v.action].append(v)


assert ACTIONS

if args.rst:
    produce_rst()

if args.python:
    produce_python()

if args.yaml:
    produce_yaml()

if args.schemas:
    produce_schemas(args.schemas)
