#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import os

import pytest

from climetlab.utils import load_json_or_yaml
from climetlab.utils import string_to_args
from climetlab.utils.humanize import as_bytes
from climetlab.utils.humanize import as_seconds
from climetlab.utils.humanize import as_timedelta
from climetlab.utils.humanize import bytes
from climetlab.utils.humanize import number
from climetlab.utils.humanize import plural
from climetlab.utils.humanize import seconds
from climetlab.utils.humanize import when


def test_load_yaml():
    filename = os.path.join(os.path.dirname(__file__), "example.yaml")
    load_json_or_yaml(filename)

    filename = os.path.join(os.path.dirname(__file__), "example.yml")
    load_json_or_yaml(filename)

    filename = os.path.join(os.path.dirname(__file__), "unknown.yml")
    with pytest.raises(FileNotFoundError):
        load_json_or_yaml(filename)

    filename = os.path.join(os.path.dirname(__file__), "example.ya_ml")
    with pytest.raises(ValueError):
        load_json_or_yaml(filename)


def test_load_json():
    filename = os.path.join(os.path.dirname(__file__), "example.json")
    load_json_or_yaml(filename)


def test_string_to_args():
    assert string_to_args("a") == ("a", [], {})
    assert string_to_args("a()") == ("a", [], {})
    assert string_to_args("a(1,2)") == ("a", [1, 2], {})
    assert string_to_args("a(1,p=2)") == ("a", [1], {"p": 2})
    assert string_to_args("a_b(q=9,p=2)") == ("a_b", [], {"q": 9, "p": 2})
    assert string_to_args("a-b(q=9,p=2)") == ("a-b", [], {"q": 9, "p": 2})
    assert string_to_args("a-b(i,j)") == ("a-b", ["i", "j"], {})
    assert string_to_args("a-b(i=2,j=9)") == ("a-b", [], {"i": 2, "j": 9})
    assert string_to_args("merge()") == ("merge", [], {})


def test_humanize():
    assert bytes(10) == "10"
    assert bytes(1024) == "1 KiB"
    assert bytes(1024 * 1024) == "1 MiB"

    assert seconds(0) == "instantaneous"
    assert seconds(0.1) == "0.1 second"
    assert seconds(0.01) == "10 milliseconds"
    assert seconds(0.001) == "1 millisecond"
    assert seconds(0.0001) == "100 microseconds"
    assert seconds(0.00001) == "10 microseconds"
    assert seconds(0.000001) == "1 microsecond"
    assert seconds(0.0000001) == "100 nanoseconds"
    assert seconds(0.00000001) == "10 nanoseconds"

    assert seconds(1) == "1 second"
    assert seconds(10) == "10 seconds"
    assert seconds(100) == "1 minute 40 seconds"
    assert seconds(1000) == "16 minutes 40 seconds"
    assert seconds(10000) == "2 hours 46 minutes 40 seconds"
    assert seconds(100000) == "1 day 3 hours 46 minutes 40 seconds"
    assert seconds(1000000) == "1 week 4 days 13 hours 46 minutes 40 seconds"

    assert number(10) == "10"
    assert number(123456) == "123,456"

    assert plural(0, "dog") == "0 dog"
    assert plural(1, "dog") == "1 dog"
    assert plural(10, "dog") == "10 dogs"
    assert plural(10000, "dog") == "10,000 dogs"

    now = datetime.datetime(2021, 9, 6, 20, 1, 0)
    assert when(now, now) == "right now"

    assert when(now, now - datetime.timedelta(seconds=1)) == "in 1 second"
    assert when(now - datetime.timedelta(seconds=1), now) == "1 second ago"

    assert when(now, now - datetime.timedelta(seconds=5)) == "in 5 seconds"
    assert when(now - datetime.timedelta(seconds=5), now) == "5 seconds ago"

    assert when(now, now - datetime.timedelta(seconds=60)) == "in 1 minute"
    assert when(now - datetime.timedelta(seconds=60), now) == "1 minute ago"

    assert when(now, now - datetime.timedelta(seconds=70)) == "in 1 minute"
    assert when(now - datetime.timedelta(seconds=70), now) == "1 minute ago"

    assert when(now, now - datetime.timedelta(seconds=300)) == "in 5 minutes"
    assert when(now - datetime.timedelta(seconds=300), now) == "5 minutes ago"

    assert when(now, now - datetime.timedelta(hours=1)) == "in 1 hour"
    assert when(now - datetime.timedelta(hours=1), now) == "1 hour ago"

    assert when(now, now - datetime.timedelta(hours=2)) == "in 2 hours"
    assert when(now - datetime.timedelta(hours=2), now) == "2 hours ago"

    assert when(now - datetime.timedelta(hours=24), now) == "yesterday at 20:01"
    assert when(now, now - datetime.timedelta(hours=24)) == "tomorrow at 20:01"

    assert when(now - datetime.timedelta(hours=90), now) == "last Friday"
    assert when(now, now - datetime.timedelta(hours=90)) == "next Monday"

    assert when(now - datetime.timedelta(hours=240), now) == "the 27th of last month"
    assert when(now, now - datetime.timedelta(hours=240)) == "in 1 month"

    assert when(now - datetime.timedelta(hours=2400), now) == "4 months ago"
    assert when(now, now - datetime.timedelta(hours=2400)) == "in 4 months"

    assert when(now - datetime.timedelta(days=90), now) == "3 months ago"
    assert when(now, now - datetime.timedelta(days=90)) == "in 3 months"

    assert when(now - datetime.timedelta(days=365), now) == "last year"
    assert when(now, now - datetime.timedelta(days=365)) == "next year"

    assert when(now - datetime.timedelta(days=900), now) == "2 years ago"
    assert when(now, now - datetime.timedelta(days=900)) == "in 2 years"

    assert when(now - datetime.timedelta(days=3660), now) == "10 years ago"
    assert when(now, now - datetime.timedelta(days=3660)) == "in 10 years"

    assert when(now - datetime.timedelta(days=3660), now, short=False) == "on Tuesday 30 September 2011"
    assert when(now, now - datetime.timedelta(days=3660), short=False) == "on Monday 6 October 2021"


def test_as_timedelta():
    assert as_timedelta("1s") == datetime.timedelta(seconds=1)
    assert as_timedelta("1S") == datetime.timedelta(seconds=1)
    assert as_timedelta("1 s") == datetime.timedelta(seconds=1)
    assert as_timedelta(" 1s") == datetime.timedelta(seconds=1)
    assert as_timedelta("1sec") == datetime.timedelta(seconds=1)
    assert as_timedelta("1second") == datetime.timedelta(seconds=1)

    with pytest.raises(ValueError):
        as_timedelta("s")

    assert as_timedelta("2m") == datetime.timedelta(minutes=2)
    assert as_timedelta("10min") == datetime.timedelta(minutes=10)
    assert as_timedelta("30 minute") == datetime.timedelta(minutes=30)
    assert as_timedelta("120 minute") == datetime.timedelta(minutes=120)

    assert as_timedelta("1h") == datetime.timedelta(hours=1)
    assert as_timedelta("25hour") == datetime.timedelta(hours=25)

    assert as_timedelta("1d") == datetime.timedelta(days=1)
    assert as_timedelta("1day") == datetime.timedelta(days=1)

    assert as_timedelta("1w") == datetime.timedelta(days=7)
    assert as_timedelta("1week") == datetime.timedelta(days=7)

    with pytest.raises(ValueError):
        print(as_timedelta("1a"))

    with pytest.raises(ValueError):
        print(as_timedelta("1a1h"))

    assert as_timedelta("1w 2d 3h 4m 5s") == datetime.timedelta(
        days=9,
        hours=3,
        minutes=4,
        seconds=5,
    )


def test_as_bytes():
    assert as_bytes("1") == 1
    assert as_bytes("1k") == 1024
    assert as_bytes("2K") == 2048
    assert as_bytes("1m") == 1024 * 1024
    assert as_bytes("1g") == 1024 * 1024 * 1024
    assert as_bytes("1t") == 1024 * 1024 * 1024 * 1024


# def test_as_percent():
#     assert as_percent("1") == 1
#     assert as_percent("1%") == 1


def test_as_seconds():
    assert as_seconds("1") == 1
    assert as_seconds("2s") == 2
    assert as_seconds("1m") == 60
    assert as_seconds("2h") == 2 * 60 * 60


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
