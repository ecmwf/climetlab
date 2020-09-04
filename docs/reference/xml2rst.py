#!/usr/bin/env python3
import sys
import xmltodict
import yaml
from collections import defaultdict, OrderedDict

yaml.Dumper.ignore_aliases = lambda *args: True

DEFS = {}
DOCS = {}

T = {
    "on": True,
    "off": False,
    "no": False,
    "stringarray()": [],
    "intarray()": [],
    "floatarray()": [],
}


def tidy(x):

    if isinstance(x, (list, tuple)):
        return [tidy(y) for y in x]

    if isinstance(x, (dict, OrderedDict)):
        d = {}
        for k, v in x.items():
            d[tidy(k)] = tidy(v)

        return d

    if isinstance(x, str):
        if x.startswith("@"):
            return x[1:]

    try:
        return int(x)
    except:
        pass

    try:
        return float(x)
    except:
        pass


    x = T.get(x, x)

    if isinstance(x, str):
        return x.strip().replace("\n", " ").replace("\t", " ").replace("  ", " ")

    return x


def load(n):
    with open(n) as f:
        x = tidy(xmltodict.parse(f.read()))

    # print(
    #     yaml.dump(
    #         tidy(x)["magics"],
    #         default_flow_style=False,
    #         default_style=None,
    #         canonical=False,
    #         explicit_start=True,
    #     )
    # )

    klass = x["magics"]["class"]
    klass["PATH"] = n

    assert klass["name"] not in DEFS, (klass["name"], n, DEFS[klass["name"]])
    DEFS[klass["name"]] = klass

    # if 'inherits' in klass:
    #     return

    # try:
    #     assert False
    #     print(klass['name'])
    # except:
    #     print(json.dumps(x, indent=4))
    #     exit(1)


for n in sys.argv[1:]:
    load(n)


def action(klass):
    if "action" in klass:
        return klass["action"]
    if "inherits" in klass:
        if "/" in klass["inherits"]:
            return [action(x) for x in klass["inherits"].split("/")]
        return action(DEFS[klass["inherits"]])


ACTIONS = defaultdict(list)

PARAMS = defaultdict(set)
for n, klass in DEFS.items():
    parms = klass.get("parameter", [])
    if not isinstance(parms, list):
        parms = [parms]

    a = action(klass)
    if a and isinstance(a, str):
        # assert isinstance(a, str), a
        DOCS[a] = str(klass.get("documentation", ""))
        for p in parms:

            try:
                PARAMS[p["name"]].add(a)
            except:
                print(klass)
                raise

            ACTIONS[a].append(p)

    # print(n, action(klass))
    # if '@action' in klass:
    #     print(n, json.dumps(klass, indent=4))
# load("Contour.xml")

# for p, v in sorted(PARAMS.items()):
#     print(p, v)

print("Plotting")
print("========")
print()

for p, v in sorted(ACTIONS.items()):
    if p[0] == p[0].upper():
        continue
    print()
    print(p)
    print("-" * len(p))
    print()
    print(DOCS.get(p, ""))
    print()
    print(".. list-table::")
    print("   :header-rows: 1")
    print("   :widths: 10 20 20 60")
    print()

    print("   * - Name")
    print("     - Type")
    print("     - Default")
    print("     - Description")

    for x in sorted(v, key=lambda p: p["name"]):
        print("   * - %s" % (x["name"],))
        if x["to"] == x["from"]:
            print("     - %s" % (x["to"],))
        else:
            print("     - %s(%s)" % (x["to"], x["from"]))

        if x["from"] == 'float':
            try:
                x["default"] = float(x["default"])
            except:
                pass
        print("     - %s" % (x.get("default", "?")))
        print("     - %s" % (x.get("documentation", "")))
