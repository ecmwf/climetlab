#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from io import StringIO
from unittest.mock import patch

import pytest

from climetlab.sources.cds import CDSAPIKeyPrompt
from climetlab.sources.mars import MARSAPIKeyPrompt
from climetlab.testing import MISSING


def test_mars_api_key():
    answers = [
        "https://api.ecmwf.int/v1",
        "b295aad8af30332fad2fa8c963ab7900",
        "joe.user@example.com",
    ]

    with patch("climetlab.sources.prompt.Text.ask", side_effect=answers):
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            prompt = MARSAPIKeyPrompt().ask_user()

    assert prompt == {
        "url": "https://api.ecmwf.int/v1",
        "key": "b295aad8af30332fad2fa8c963ab7900",
        "email": "joe.user@example.com",
    }

    printed = stdout.getvalue().strip()
    assert printed.startswith("An API key is needed to access this dataset.")


def test_cds_api_key():
    answers = [
        "https://cds.climate.copernicus.eu/api/v2",
        "123:abcdef01-0000-1111-2222-0123456789ab",
    ]

    with patch("climetlab.sources.prompt.Text.ask", side_effect=answers):
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            prompt = CDSAPIKeyPrompt().ask_user()

    assert prompt == {
        "url": "https://cds.climate.copernicus.eu/api/v2",
        "key": "123:abcdef01-0000-1111-2222-0123456789ab",
    }

    printed = stdout.getvalue().strip()
    assert printed.startswith("An API key is needed to access this dataset.")


@pytest.mark.skipif(
    MISSING("climetlab_eumetsat"),
    reason="climetlab-eumetsat not installed",
)
def test_eumetsat_api_key():
    from climetlab_eumetsat.eumetsat import EumetsatAPIKeyPrompt

    answers = [
        "aEfX6e1AvizULa48eo9R1v9A56md",
        "Uiaz51e8XAfmA969o1vR4aELdev6",
    ]

    with patch("climetlab.sources.prompt.Text.ask", side_effect=answers):
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            prompt = EumetsatAPIKeyPrompt().ask_user()

    assert prompt == {
        "consumer_key": "aEfX6e1AvizULa48eo9R1v9A56md",
        "consumer_secret": "Uiaz51e8XAfmA969o1vR4aELdev6",
    }

    printed = stdout.getvalue().strip()
    assert printed.startswith("An API key is needed to access this dataset.")


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
