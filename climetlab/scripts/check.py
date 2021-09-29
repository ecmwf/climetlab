# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import os
from importlib import import_module

from termcolor import colored


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

    def do_versions(self, args):
        from importlib.metadata import PackageNotFoundError, version

        import entrypoints

        modules = [x.strip() for x in args.split(" ") if x.strip()]
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

        plugins = set()
        for kind in ("source", "dataset"):
            for e in entrypoints.get_group_all(f"climetlab.{kind}s"):
                plugins.add(e.module_name.split(".")[0])

        for module in sorted(list(modules) + list(plugins)):
            try:
                print(module, colored(version(module), "green"))
            except PackageNotFoundError:
                print(module, colored("missing", "red"))

    def do_libraries(self, args):

        try:
            import Magics

            print("magics", colored(Magics.lib, "green"))
        except Exception as e:
            print("magics", colored(e, "red"))

        try:
            import gribapi

            print("eccodes", colored(gribapi.library_path, "green"))
        except Exception as e:
            print("eccodes", colored(e, "red"))
