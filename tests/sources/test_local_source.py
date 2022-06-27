import os

import climetlab as cml

here = os.path.dirname(__file__)


def test_a():
    s = cml.load_source("local", os.path.join(here, "gribs", "a"), param="t")
    s = cml.load_source(
        "local", os.path.join(here, "gribs", "a"), param="t", level="1000"
    )
    print(s, len(s))
    ds = s.to_xarray()
    print(ds)


def test_b():
    s = cml.load_source(
        "local", os.path.join(here, "gribs", "b"), param="2t", realization="0"
    )
    print(s, len(s))
    ds = s.to_xarray()
    print(ds)


def test_c():
    s = cml.load_source(
        "local", os.path.join(here, "gribs", "c"), param="2t", realization="0"
    )
    print(s, len(s))
    ds = s.to_xarray()
    print(ds)


if __name__ == "__main__":
    test_a()
