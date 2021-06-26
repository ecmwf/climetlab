import logging
import os
from importlib import import_module

LOG = logging.getLogger(__name__)


def data_file(name):
    return os.path.join(os.path.dirname(__file__), "data", name)


def is_package_installed(package):
    """return true if all packages in "package" are installed"""
    if isinstance(package, (list, tuple)):
        installed = [p for p in package if is_package_installed(p)]
        if len(installed) != len(package):
            return False
        return True

    try:
        import_module(package)
        return True
    except ImportError:
        return False


def main(globals):
    logging.basicConfig(level=logging.DEBUG)
    for k, f in sorted(globals.items()):
        if k.startswith("test_") and callable(f):
            LOG.debug("Running '%s'", k)
            f()
