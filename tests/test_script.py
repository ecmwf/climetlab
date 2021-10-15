# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import inspect
import logging

import pytest

from climetlab.scripts.main import CliMetLabApp

LOG = logging.getLogger(__name__)


def command_list():
    commands = [
        name
        for name, _ in inspect.getmembers(CliMetLabApp(), predicate=inspect.ismethod)
    ]
    return [name[3:] for name in commands if name.startswith("do_")]


@pytest.mark.parametrize("command", command_list())
def test_cli_no_args(command, capsys):
    app = CliMetLabApp()
    app.onecmd(command)
    out, err = capsys.readouterr()
    assert not out.startswith("Unknown command"), out
    assert err == "", err


def test_cli_unknown(capsys):
    app = CliMetLabApp()
    app.onecmd("some unknown command")
    out, err = capsys.readouterr()
    assert out.startswith("Unknown command"), out
    assert err == "", err


def test_cli_cache(capsys):
    app = CliMetLabApp()
    app.onecmd("cache")
    out, err = capsys.readouterr()
    assert out.startswith("Cache directory"), out
    assert err == "", err


if __name__ == "__main__":
    from climetlab.testing import main

    LOG.debug(f"Skipping {__file__} tests: must run with pytest because they use capsys fixture.")

    # main(globals())
