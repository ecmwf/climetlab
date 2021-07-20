#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import re
import sys

import pytest

from climetlab.testing import IN_GITHUB, climetlab_file

# See https://www.blog.pythonlibrary.org/2018/10/16/testing-jupyter-notebooks/


EXAMPLES = climetlab_file("docs", "examples")

SKIP = (
    "11-icoads.ipynb",
    # "09-weatherbench.ipynb",
)

MARS = (
    "04-source-mars.ipynb",
    "08-mars-odb.ipynb",
    "11-icoads.ipynb",
)

CDS = (
    "03-source-cds.ipynb",
    "06-era5-temperature.ipynb",
    "05-high-lows.ipynb",
    "14-gruan.ipynb",
    "11-hurricane-database.ipynb",
)


TENSORFLOW = ("05-high-lows.ipynb",)


def notebooks_list():

    notebooks = []
    for path in os.listdir(EXAMPLES):
        if re.match(r"^\d\d-.*\.ipynb$", path):
            if "Copy" not in path:
                notebooks.append(path)

    return sorted(notebooks)


@pytest.mark.skipif(not IN_GITHUB, reason="Not on GITHUB")
@pytest.mark.skipif(
    sys.platform == "win32", reason="Cannot execute notebooks on Windows"
)
@pytest.mark.parametrize("path", notebooks_list())
def test_notebook(path):
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor

    if path in SKIP:
        pytest.skip("Notebook marked as 'skip'")

    if path in MARS:
        if not os.path.exists(os.path.expanduser("~/.ecmwfapirc")):
            pytest.skip("No ~/.ecmwfapirc")

    if path in CDS:
        if not os.path.exists(os.path.expanduser("~/.cdsapirc")):
            pytest.skip("No ~/.cdsapirc")

    # if path in TENSORFLOW:
    #     if sys.version_info >= (3, 9):
    #         pytest.skip("Tensorflow not yet ready on 3.9")

    with open(os.path.join(EXAMPLES, path)) as f:
        nb = nbformat.read(f, as_version=4)

    proc = ExecutePreprocessor(timeout=60 * 60 * 5, kernel_name="python3")
    proc.preprocess(nb, {"metadata": {"path": EXAMPLES}})


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
