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

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

# See https://www.blog.pythonlibrary.org/2018/10/16/testing-jupyter-notebooks/


EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "examples")

SKIP = ("11-icoads.ipynb",)

MARS = (
    "04-source-mars.ipynb",
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


@pytest.mark.skipif(
    int(os.environ.get("CLIMETLAB_SKIP_NOTEBOOKS_TESTS", 0)),
    reason="CLIMETLAB_SKIP_NOTEBOOKS_TESTS not zero",
)
@pytest.mark.skipif(
    sys.platform == "win32", reason="Cannot execute notebookds on Windows"
)
@pytest.mark.parametrize("path", notebooks_list())
def test_notebook(path):

    if path in SKIP:
        pytest.skip("Notebook marked as 'skip'")

    if path in MARS:
        if not os.path.exists(os.path.expanduser("~/.ecmwfapirc")):
            pytest.skip("No ~/.ecmwfapirc")

    if path in CDS:
        if not os.path.exists(os.path.expanduser("~/.cdsapirc")):
            pytest.skip("No ~/.cdsapirc")

    if path in TENSORFLOW:
        if sys.version_info >= (3, 9):
            pytest.skip("Tensorflow not yet ready on 3.9")

    with open(os.path.join(EXAMPLES, path)) as f:
        nb = nbformat.read(f, as_version=4)

    proc = ExecutePreprocessor(timeout=60 * 60, kernel_name="python3")
    proc.preprocess(nb, {"metadata": {"path": EXAMPLES}})
