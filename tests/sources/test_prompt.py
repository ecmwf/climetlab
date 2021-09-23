#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from getpass import getpass
from io import StringIO
from unittest.mock import *


# @patch(
#     "builtins.input",
#     side_effect=[
#         "https://api.ecmwf.int/v1",
#         "joe.user@example.com",
#     ],
# )
# @patch(
#     "getpass.getpass",
#     side_effect=[
#         "b295aad8af30332fad2fa8c963ab7900",
#     ],
# )
def test_mars_api_key():

    shown = ["https://api.ecmwf.int/v1", "joe.user@example.com"]
    hidden = ["b295aad8af30332fad2fa8c963ab7900"]

    with patch("builtins.input", side_effect=shown):
        with patch("getpass.getpass", side_effect=hidden) as getpass:
            print(getpass, getpass.side_effect)

            with patch("sys.stdout", new_callable=StringIO) as stdout:

                from climetlab.sources.mars import MARSAPIKeyPrompt

                prompt = MARSAPIKeyPrompt().ask_user()

    assert prompt == {
        "url": "https://api.ecmwf.int/v1",
        "key": "b295aad8af30332fad2fa8c963ab7900",
        "email": "joe.user@example.com",
    }

    printed = stdout.getvalue().strip()
    assert printed.startswith("An API key is needed to access this dataset.")


def test_cds_api_key():

    shown = ["https://cds.climate.copernicus.eu/api/v2"]
    hidden = ["123:abcdef01-0000-1111-2222-0123456789ab"]

    with patch("builtins.input", side_effect=shown):
        with patch("getpass.getpass", side_effect=hidden) as getpass:
            print(getpass, getpass.side_effect)

            with patch("sys.stdout", new_callable=StringIO) as stdout:

                from climetlab.sources.cds import CDSAPIKeyPrompt

                prompt = CDSAPIKeyPrompt().ask_user()

    assert prompt == {
        "url": "https://cds.climate.copernicus.eu/api/v2",
        "key": "123:abcdef01-0000-1111-2222-0123456789ab",
    }

    printed = stdout.getvalue().strip()
    assert printed.startswith("An API key is needed to access this dataset.")


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
