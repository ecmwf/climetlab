import logging
import os
import pathlib
from importlib import import_module

from climetlab import load_source
from climetlab.readers.unknown import Unknown
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


def MISSING(*modules):
    return not modules_installed(*modules)


UNSAFE_SAMPLES_URL = "https://github.com/jwilk/traversal-archives/releases/download/0"


def empty(ds):
    assert isinstance(ds, EmptySource)


def unknown(ds):
    assert isinstance(ds._reader, Unknown)


UNSAFE_SAMPLES = (
    ("absolute1", empty),
    ("absolute2", empty),
    ("relative0", empty),
    ("relative2", empty),
    ("symlink", unknown),
    ("dirsymlink", unknown),
    ("dirsymlink2a", unknown),
    ("dirsymlink2b", unknown),
)


def check_unsafe_archives(extension):
    for archive, check in UNSAFE_SAMPLES:
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
