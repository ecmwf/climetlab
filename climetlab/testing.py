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
from importlib import import_module

from climetlab import load_source
from climetlab.readers.text import TextReader
from climetlab.sources.empty import EmptySource

LOG = logging.getLogger(__name__)


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
    for module in modules:
        try:
            import_module(module)
        except ImportError:
            return False
    return True


NO_MARS = not os.path.exists(os.path.expanduser("~/.ecmwfapirc"))
NO_CDS = not os.path.exists(os.path.expanduser("~/.cdsapirc"))
IN_GITHUB = os.environ.get("GITHUB_WORKFLOW") is not None


def MISSING(*modules):
    return not modules_installed(*modules)


UNSAFE_SAMPLES_URL = "https://github.com/jwilk/traversal-archives/releases/download/0"
TEST_DATA_URL = "https://get.ecmwf.int/repository/test-data/climetlab"


def empty(ds):
    LOG.debug("%s", ds)
    assert isinstance(ds, EmptySource)


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


def main(globals):
    import sys

    if not (len(sys.argv) > 1 and sys.argv[1] != "--no-debug"):
        logging.basicConfig(level=logging.DEBUG)

    for k, f in sorted(globals.items()):
        if k.startswith("test_") and callable(f):
            skip = None
            if hasattr(f, "pytestmark"):
                for m in f.pytestmark:
                    if m.name == "skipif" and m.args[0] is True:
                        skip = m.kwargs.get("reason", "?")
            if skip:
                LOG.debug("========= Skipping '%s' %s", k, skip)
            else:
                LOG.debug("========= Running '%s'", k)
                f()
