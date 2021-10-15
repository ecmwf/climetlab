# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.scripts.main import CliMetLabApp


def test_cli_unknown(capsys):
    app = CliMetLabApp()
    app.onecmd("cache")
    out, err = capsys.readouterr()
    assert out.startswith("Unknown command")


def test_cli_cache(capsys):
    app = CliMetLabApp()
    app.onecmd("cache")
    out, err = capsys.readouterr()
    assert out.startswith("Cache directory")


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
