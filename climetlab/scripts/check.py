# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import itertools
import json
import os
from importlib import import_module

from termcolor import colored

from .parse import parse_args


class CheckCmd:
    def do_check(self, args):
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
                    f"  {name} from ecwmlibs: ok {versions[name]} ({ecmwflibs.find(name)})"
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

    def do_plugins(self, args):
        from importlib.metadata import PackageNotFoundError, version

        import entrypoints

        result = []
        for kind in ("source", "dataset"):
            for e in entrypoints.get_group_all(f"climetlab.{kind}s"):
                module = e.module_name.split(".")[0]
                try:
                    v = version(module)
                except PackageNotFoundError:
                    v = "unknown"
                result.append((kind, e.name, e.module_name, v))

        for n in sorted(result):
            print(n)

    @parse_args(json=True, positional="*")
    def do_versions(self, args):

        """List the versions of important Python packages."""

        from importlib.metadata import PackageNotFoundError, version

        import entrypoints

        modules = args.args
        plugins = set()

        if not modules:
            modules = (
                "climetlab",
                "xarray",
                "numpy",
                "tensorflow",
                "requests",
                "cdsapi",
                "cfgrib",
                "findlibs",
                "ecmwflibs",
                "netcdf4",
                "dask",
                "zarr",
                "s3fs",
                "ecmwf-api-client",
                "eccodes",
                "magics",
                "pdbufr",
                "pyodc",
                "pandas",
                "metview",
            )
            for kind in ("source", "dataset"):
                for e in entrypoints.get_group_all(f"climetlab.{kind}s"):
                    plugins.add(e.module_name.split(".")[0])
        result = {}

        for module in itertools.chain(modules, plugins):
            try:
                result[module] = version(module)
            except PackageNotFoundError:
                result[module] = "missing"

        if args.json:
            print(json.dumps(result, indent=4, sort_keys=True))
        else:
            for k, v in sorted(result.items()):
                print(k, colored(v, "red" if v == "missing" else "green"))

    @parse_args(json=True)
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
            for k, v in sorted(result.items()):
                print(k, colored(v, "green" if os.path.exists(v) else "red"))
