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

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

# See https://www.blog.pythonlibrary.org/2018/10/16/testing-jupyter-notebooks/


EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "examples")


def notebooks_list():

    notebooks = []
    for path in os.listdir(EXAMPLES):
        if re.match(r"^\d\d-.*\.ipynb$", path):
            if "Copy" not in path:
                notebooks.append(path)

    return sorted(notebooks)


@pytest.mark.parametrize("path", notebooks_list())
def test_notebook(path):

    with open(os.path.join(EXAMPLES, path)) as f:
        nb = nbformat.read(f, as_version=4)

    proc = ExecutePreprocessor(timeout=600, kernel_name="python3")
    proc.preprocess(nb, {"metadata": {"path": EXAMPLES}})
