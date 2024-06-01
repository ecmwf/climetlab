# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import tempfile


class TmpFile:
    """The TmpFile objets are designed to be used for temporary files.
    It ensures that the file is unlinked when the object is
    out-of-scope (with __del__).

    Parameters
    ----------
    path : str
        Actual path of the file.
    """

    def __init__(self, path: str):
        self.path = path

    def __del__(self):
        self.cleanup()

    def __enter__(self):
        return self.path

    def __exit__(self, *args, **kwargs):
        self.cleanup()

    def cleanup(self):
        if self.path is not None and os is not None:
            os.unlink(self.path)
        self.path = None


def temp_file(extension=".tmp") -> TmpFile:
    """Create a temporary file with the given extension.

    Parameters
    ----------
    extension : str, optional
        By default ".tmp"

    Returns
    -------
    TmpFile
    """

    fd, path = tempfile.mkstemp(suffix=extension)
    os.close(fd)
    return TmpFile(path)


class TmpDirectory(tempfile.TemporaryDirectory):
    @property
    def path(self):
        return self.name


def temp_directory():
    return TmpDirectory()


class TmpEnv:
    """
    A context manager that temporarily sets environment variables.

    Usage:
    >>> import os
    >>> with TmpEnv(CLIMETLAB_TESTS_FOO='123', CLIMETLAB_TESTS_BAR='456'):
    ...     print(os.environ['CLIMETLAB_TESTS_FOO'])
    ...     print(os.environ['CLIMETLAB_TESTS_BAR'])
    123
    456
    >>> print(os.environ.get('CLIMETLAB_TESTS_FOO'))
    None
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.previous = {}

    def __enter__(self):
        for key, value in self.kwargs.items():
            self.previous[key] = os.environ.get(key)
            os.environ[key] = str(value)

    def __exit__(self, type, value, traceback):
        for key in self.kwargs.keys():
            if self.previous.get(key) is not None:
                os.environ[key] = self.previous[key]
            else:
                del os.environ[key]


def temp_env(**kwargs):
    return TmpEnv(**kwargs)
