# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os
import pathlib
import shutil
from contextlib import contextmanager
from unittest.mock import patch

from climetlab import load_source
from climetlab.readers.text import TextReader
from climetlab.sources.empty import EmptySource
from climetlab.utils import download_and_cache, module_installed

LOG = logging.getLogger(__name__)


class OfflineError(Exception):
    pass


_NETWORK_PATCHER = patch("socket.socket", side_effect=OfflineError)


@contextmanager
def network_off():
    try:
        _NETWORK_PATCHER.start()
        yield None
    finally:
        _NETWORK_PATCHER.stop()


def climetlab_file(*args):
    top = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(top, *args)


def data_file(*args):
    return os.path.join(os.path.dirname(__file__), "data", *args)


def file_url(path):
    return pathlib.Path(os.path.abspath(path)).as_uri()


def data_file_url(*args):
    return file_url(data_file(*args))


def modules_installed(*modules):
    return all(module_installed(m) for m in modules)


NO_MARS = not os.path.exists(os.path.expanduser("~/.ecmwfapirc"))
NO_CDS = not os.path.exists(os.path.expanduser("~/.cdsapirc"))
IN_GITHUB = os.environ.get("GITHUB_WORKFLOW") is not None
NO_EOD = not os.path.exists(os.path.expanduser("~/.ecmwf-open-data"))


def MISSING(*modules):
    return not modules_installed(*modules)


UNSAFE_SAMPLES_URL = "https://github.com/jwilk/traversal-archives/releases/download/0"
TEST_DATA_URL = "https://get.ecmwf.int/repository/test-data/climetlab"
TEST_DATA_URL_INPUT_GRIB = TEST_DATA_URL + "/test-data/input/grib"


def empty(ds):
    LOG.debug("%s", ds)
    assert isinstance(ds, EmptySource)
    assert len(ds) == 0


def text(ds):
    LOG.debug("%s", ds)
    assert isinstance(ds._reader, TextReader)


UNSAFE_SAMPLES = (
    ("absolute1", empty),
    ("absolute2", empty),
    ("relative0", empty),
    ("relative2", empty),
    ("symlink", text),
    ("dirsymlink", text),
    ("dirsymlink2a", text),
    ("dirsymlink2b", text),
)


def check_unsafe_archives(extension):
    for archive, check in UNSAFE_SAMPLES:
        LOG.debug("%s.%s", archive, extension)
        ds = load_source("url", f"{UNSAFE_SAMPLES_URL}/{archive}{extension}")
        check(ds)


def build_testdata(dir="testdata"):
    os.makedirs(dir, exist_ok=True)
    for path in [
        "2t-tp.grib",
        "all.grib",
        "all/climetlab.json",
        "all/u.grib",
        "all/v.grib",
        "all/z.grib",
        "all/2t.grib",
        "all/climetlab.json",
        "all/tp.grib",
        "all/lsm.grib",
        "climetlab.json",
        "lsm.grib",
        "pl/climetlab.json",
        "pl/u.grib",
        "pl/v.grib",
        "pl/z.grib",
        "sfc/2t.grib",
        "sfc/climetlab.json",
        "sfc/tp.grib",
        "uvz.grib",
        "uvz-20150418.grib",
    ]:
        outpath = os.path.join(dir, path)
        if os.path.exists(outpath):
            continue
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        shutil.copyfile(
            download_and_cache(TEST_DATA_URL_INPUT_GRIB + "/" + path), outpath
        )

    return dir


@contextmanager
def cd(dir):
    old = os.getcwd()
    os.chdir(os.path.expanduser(dir))
    try:
        yield dir
    finally:
        os.chdir(old)


def main(path):
    import sys

    import pytest

    # Parallel does not work on darwin, gets RuntimeError: context has already been set
    # because pytest-parallel changes the context from `spawn` to `fork`

    args = ["-p", "no:parallel", "-E", "release"]

    if len(sys.argv) > 1 and sys.argv[1] == "--no-debug":
        args += ["-o", "log_cli=False"]
    else:
        logging.basicConfig(level=logging.DEBUG)
        args += ["-o", "log_cli=True"]

    args += [path]

    sys.exit(pytest.main(args))
