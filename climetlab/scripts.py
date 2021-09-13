import os
import sys
from importlib import import_module

import climetlab


def check():
    print(
        (
            "This script is experimental to help debugging."
            "Seeing everything to 'ok' does NOT means that you have the right versions installed."
        )
    )
    print("--------------------")

    print("Checking climetlab installation.")
    print(f"Climetlab installed in {os.path.dirname(climetlab.__file__)}")
    print("Checking required compiled dependencies...")
    import ecmwflibs

    versions = ecmwflibs.versions()

    for name in ["eccodes", "magics"]:
        print(f"{name}: ok {versions[name]} ({ecmwflibs.find(name)})")

    print("Checking required python dependencies...")
    for name in ["xarray", "eccodes", "ecmwflibs"]:
        lib = import_module(name)
        print(f"{name}: ok {lib.__version__} ({os.path.dirname(lib.__file__)})")

    print("Checking optional dependencies...")
    for name in ["folium", "pdbufr", "pyodc"]:
        try:
            lib = import_module(name)
            print(f"{name}: ok {lib.__version__} ({os.path.dirname(lib.__file__)})")
        except Exception as e:
            print(e)
            print(f"Warning: cannot import {name}. Limited capabilities.")

    # TODO: add more
    # TODO: automate this from requirements.txt. Create a pip install climetlab[extra] or climetlab-light.


def main_climetlab():
    if sys.argv and sys.argv[1] == "check":
        check()


if __name__ == "__main__":
    main_climetlab()
