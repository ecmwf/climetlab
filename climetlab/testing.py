import logging
import os
import pathlib
from importlib import import_module

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


def main(globals):
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