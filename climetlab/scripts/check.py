# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import json
import os
import re
import sys
from importlib import import_module

from termcolor import colored

from .tools import experimental, parse_args, print_table


def version(module):
    try:
        from importlib.metadata import PackageNotFoundError, version
    except Exception:
        from importlib_metadata import PackageNotFoundError, version

    try:
        return version(module)
    except PackageNotFoundError:
        pass

    try:

        module = import_module(module)

        if not hasattr(module, "__file__") or module.__file__ is None:

            if not hasattr(module, "__path__"):
                return "builtin"

            return "namespace"

        if hasattr(module, "__version__"):
            return str(module.__version__)

        if hasattr(module, "version"):
            return str(module.version)

        path = os.path.realpath(module.__file__)
        if os.path.basename(path) == "__init__.py":
            path = os.path.dirname(path)

        directory = os.path.basename(os.path.dirname(path))
        if directory == "lib-dynload":
            directory = os.path.basename(os.path.dirname(os.path.dirname(path)))
        if re.fullmatch(r"python\d+\.\d+", directory):
            return directory

        return module.__file__

    except ImportError:
        return "missing"
    except Exception as e:
        return e


class CheckCmd:
    @parse_args()
    @experimental
    def do_check(self, args):
        """Experimental script to help debugging."""
        import climetlab

        print(
            colored(
                (
                    "This script is experimental to help debugging."
                    "Seeing everything to 'ok' does NOT means that you have the right versions installed."
                ),
                "red",
            )
        )

        print("--------------------")

        print("Checking climetlab installation.")
        print(f"Climetlab installed in {os.path.dirname(climetlab.__file__)}")
        print("Checking required compiled dependencies...")

        import ecmwflibs

        versions = ecmwflibs.versions()

        for name in ["eccodes", "magics"]:
            try:
                print(
                    f"  {name} from ecmwflibs: ok {versions[name]} ({ecmwflibs.find(name)})"
                )
            except Exception as e:  # noqa: F841
                print(f"  {name} from ecmwflib: Warning: ecmwflibs cannot find {name}")

        for name in ["eccodes", "MagPlus", "netcdf"]:
            try:
                import findlibs
            except Exception as e:  # noqa: F841
                print(f"    {name} from findlibs: Warning: cannot import findlibs")
                continue
            try:
                print(f"    {name} from findlibs: ({findlibs.find(name)})")
            except Exception as e:  # noqa: F841
                print(f"    {name} from findlibs: Warning: findlibs cannot find {name}")

        print("Checking required python dependencies...")
        for name in ["xarray", "Magics", "eccodes", "ecmwflibs"]:
            more = ""
            try:
                lib = import_module(name)
            except ImportError:
                print(f"  Error: cannot import {name}.")
                continue
            # if name == "eccodes":
            #     more = f" (using .lib={lib.lib})"
            print(
                f"  {name}: ok {lib.__version__} ({os.path.dirname(lib.__file__)}){more}"
            )

        print("Checking optional dependencies...")
        for name in ["folium", "pdbufr", "pyodc"]:
            try:
                lib = import_module(name)
                print(
                    f"  {name}: ok {lib.__version__} ({os.path.dirname(lib.__file__)})"
                )
            except Exception as e:
                print(e)
                print(f"  Warning: cannot import {name}. Limited capabilities.")

        # TODO: add more
        # TODO: automate this from requirements.txt. Create a pip install climetlab[extra] or climetlab-light.

    @parse_args(
        json=dict(action="store_true", help="produce a JSON output"),
    )
    def do_plugins(self, args):
        """List the available plugins"""

        import entrypoints

        plugins = []
        for kind in ("source", "dataset"):
            for e in entrypoints.get_group_all(f"climetlab.{kind}s"):
                module = e.module_name.split(".")[0]
                plugins.append((kind, e.name, e.module_name, version(module)))

        if args.json:
            result = {}
            for n in plugins:
                result[n[1]] = dict(type=n[0], module=n[2], version=n[3])
            print(json.dumps(result, indent=4, sort_keys=True))
            return

        for n in sorted(plugins):
            print(n[0], n[1])
            print("  module:", n[2], "version:", n[3])
            print()

    def _loaded_modules(self, name):
        import pkgutil

        loader = pkgutil.get_loader(name)
        path = os.path.realpath(loader.path)
        if os.path.isfile(path):
            path = os.path.dirname(path)

        modules = set()
        for root, _, files in os.walk(path):
            for file in files:
                if not file.endswith(".py"):
                    continue
                full = os.path.join(root, file)
                with open(full, "rt") as f:
                    for line in f.readlines():
                        line = line.strip()
                        if line.startswith("import ") or line.startswith("from "):
                            module = line.split(" ")[1].split(".")[0]
                            if module:
                                modules.add(module)

        modules.add("dask")
        modules.add("distributed")
        modules.add("asyncssh")
        return modules

    @parse_args(
        modules=(
            "modules",
            dict(
                metavar="PACKAGE",
                type=str,
                nargs="*",
                help="optional list of Python packages",
            ),
        ),
        json=dict(action="store_true", help="produce a JSON output"),
        all=dict(action="store_true"),
    )
    def do_versions(self, args):

        """List the versions of important Python packages."""
        import entrypoints

        modules = set(args.modules)

        if not modules:
            modules = self._loaded_modules("climetlab")
            seen = set()
            for kind in ("source", "dataset"):
                for e in entrypoints.get_group_all(f"climetlab.{kind}s"):
                    name = e.module_name.split(".")[0]
                    if name not in seen:
                        modules.update(self._loaded_modules(name))
                        seen.add(name)

        result = {}

        if args.all:
            for module in modules:
                try:
                    import_module(module)
                except Exception:
                    pass
            modules.update(sys.modules.keys())

        modules = set(m.split(".")[0] for m in modules if not m.startswith("_"))

        for module in modules:
            result[module] = version(module)

        if args.json:
            print(json.dumps(result, indent=4, sort_keys=True))
        else:
            COLORS = dict(
                missing="red", damaged="red", builtin="blue", namespace="magenta"
            )
            items = []
            colours = []
            for k, v in sorted(result.items()):
                items.append((k, v))
                if not isinstance(v, str):
                    v = str(v)
                    c = "red"
                else:
                    c = "yellow" if v.startswith("python") else "green"

                colours.append(COLORS.get(v, c))

            print_table(items, colours)

    @parse_args(
        json=dict(action="store_true", help="produce a JSON output"),
    )
    def do_libraries(self, args):

        result = {}
        try:
            import Magics

            result["magics"] = os.path.realpath(Magics.lib)
        except Exception as e:
            result["magics"] = str(e)

        try:
            import gribapi

            result["eccodes"] = os.path.realpath(gribapi.library_path)
        except Exception as e:
            result["eccodes"] = str(e)

        if args.json:
            print(json.dumps(result, indent=4, sort_keys=True))
        else:
            items = []
            colours = []
            for k, v in sorted(result.items()):
                items.append((k, v))
                colours.append("green" if os.path.exists(v) else "red")

            print_table(items, colours)

    def do_df(self, path):
        from climetlab.core.caching import disk_usage

        if path == "-h":
            print("Provide some information about disk usage.")
            return

        print(disk_usage(path))
