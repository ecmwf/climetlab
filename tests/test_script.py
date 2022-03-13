# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import re

import pytest
import yaml

from climetlab import settings
from climetlab.scripts.main import CliMetLabApp

LOG = logging.getLogger(__name__)


def command_list():
    return [
        func[3:]
        for func in dir(CliMetLabApp)
        if callable(getattr(CliMetLabApp, func))
        and func.startswith("do_")
        and getattr(CliMetLabApp, func).__module__.startswith("climetlab.")
    ]


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


def test_cli_setting_1(capsys):
    app = CliMetLabApp()
    app.onecmd("settings --json")
    out, err = capsys.readouterr()
    assert err == "", err

    # yaml is a superset of json. yaml.safe_load can read json
    dic = yaml.safe_load(out)

    assert len(dic) > 2

    for s in settings.dump():
        assert dic[s[0]] == s[1]


def do_nothing(text, *args, **kwargs):
    assert 0
    return text


@pytest.fixture
def settings_dict():
    return {s[0]: s[1] for s in settings.dump()}


def test_cli_setting_2(capsys, settings_dict):
    app = CliMetLabApp()
    app.onecmd("settings")
    out, err = capsys.readouterr()
    assert err == "", err

    lines = out.splitlines(True)
    assert lines

    for line in lines:
        assert line
        m = re.match("([^ ]*) *([^ ]+)", line)
        assert m is not None, line
        key = m.groups()[0]
        key = key.strip()
        value = m.groups()[1]
        # TODO: replace the following line by stripping colorcodes or add an option --no-color
        value = value.strip()[5:-4]
        assert key in settings_dict
        assert value == str(settings_dict[key])


def test_cli_df(capsys):
    app = CliMetLabApp()
    app.onecmd("df")
    out, err = capsys.readouterr()
    assert out.startswith("DiskUsage("), out
    assert err == "", err


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
