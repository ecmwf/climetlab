import sys


def check():
    print("Checking climetlab installation.")
    print("Checking required dependencies...")
    import xarray  # noqa: F401

    print("xarray: ok")
    import pandas  # noqa: F401

    print("pandas: ok")
    # TODO: add more
    # print('All required dependencies seems to be ok.')

    print("Checking optional dependencies...")
    try:
        import pdbufr  # noqa: F401
    except Exception as e:
        print(e)
        print("Warning: cannot import pdbufr. Limited capabilities.")
    try:
        import pyodc  # noqa: F401
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
