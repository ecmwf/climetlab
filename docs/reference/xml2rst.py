#!/usr/bin/env python3
import sys
import xmltodict
import yaml
from collections import defaultdict, OrderedDict

yaml.Dumper.ignore_aliases = lambda *args: True

DEFS = OrderedDict()

T = {
    "on": True,
    "off": False,
    "no": False,
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

        return repr(default)

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


for n in sys.argv[1:]:
    load(n)

for v in DEFS.values():
    v.inherits

ACTIONS = defaultdict(list)
for k, v in DEFS.items():
    if not v._super:
        if v.action is not None:
            ACTIONS[v.action].append(v)

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
    # print("     - Description")

    for k in klasses:

        for p in k.parameters:
            print("   * - |", "**%s**" % p.name)
            print("       |", p.documentation)
            print("     - |", p.values)
            print("     - |", p.default)
            # print("     -", p.documentation)
    print()


# for p, v in sorted(ACTIONS.items()):
#     if p[0] == p[0].upper():
#         continue
#     print()
#     print(p)
#     print("-" * len(p))
#     print()
#     print(DOCS.get(p, ""))
#     print()
#     print(".. list-table::")
#     print("   :header-rows: 1")
#     print("   :widths: 10 20 20 60")
#     print()

#     print("   * - Name")
#     print("     - Type")
#     print("     - Default")
#     print("     - Description")

#     for x in sorted(v, key=lambda p: p["name"]):
#         print("   * - %s" % (x["name"],))

#         if "values" in x:
#             print("     - %s" % (", ".join([repr(y) for y in x["values"].split("/")])))
#         else:
#             if x["to"] == x["from"]:
#                 print("     - %s" % (x["to"],))
#             else:
#                 print("     - %s(%s)" % (x["to"], x["from"]))

#         if x["from"] == "float":
#             try:
#                 x["default"] = float(x["default"])
#             except:
#                 pass
#         print("     - %r" % (x.get("default", "?")))
#         print("     - %s" % (x.get("documentation", "")))
