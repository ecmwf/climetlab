import os
import sys

import climetlab


def check():
    print("Checking climetlab installation.")
    print(f"Climetlab installed in {os.path.dirname(climetlab.__file__)}")
    print("Checking required dependencies...")
    import xarray  # noqa: F401

    print(f"xarray: ok ({os.path.dirname(xarray.__file__)})")
    import pandas  # noqa: F401

    print(f"pandas: ok ({os.path.dirname(pandas.__file__)})")
    # TODO: add more
    # print('All required dependencies seems to be ok.')

    print("Checking optional dependencies...")
    try:
        import pdbufr  # noqa: F401

        print(f"pdbufr: ok ({os.path.dirname(pdbufr.__file__)})")
    except Exception as e:
        print(e)
        print("Warning: cannot import pdbufr. Limited capabilities.")
    try:
        import pyodc  # noqa: F401

        print(f"pyodc: ok ({os.path.dirname(pyodc.__file__)})")
    except Exception as e:
        print(e)
        print("Warning: cannot import pyodc. Limited capabilities.")
    # TODO: add more
    # TODO: automate this from requirements.txt. Create a pip install climetlab[extra] or climetlab-light.


def main_climetlab():
    if sys.argv and sys.argv[1] == "check":
        check()


if __name__ == "__main__":
    main_climetlab()
