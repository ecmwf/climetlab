# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


def bytes_to_string(n):
    u = ["", " KiB", " MiB", " GiB", " TiB", " PiB"]
    i = 0
    while n >= 1024:
        n /= 1024.0
        i += 1
    return "%g%s" % (int(n * 10 + 0.5) / 10.0, u[i])


PERIODS = (
    (7 * 24 * 60 * 60, "week"),
    (24 * 60 * 60, "day"),
    (60 * 60, "hour"),
    (60, "minute"),
    (1, "second"),
)


def _plural(count):
    if count > 1:
        return "s"
    else:
        return ""


def seconds_to_english(seconds):
    if seconds < 0.1:
        units = [
            "milli",
            "micro",
            "nano",
            "pico",
            "femto",
            "atto",
            "zepto",
            "yocto",
        ]
        i = 0
        while seconds < 1.0 and i < len(units) - 1:
            seconds *= 1000
            i += 1
        if seconds > 100 and i > 0:
            seconds /= 1000
            i -= 1
        seconds = round(seconds * 10) / 10
        return f"{seconds:g} {units[i]}second{_plural(seconds)}"

    n = seconds
    s = []
    for p in PERIODS:
        m = int(n / p[0])
        if m:
            s.append("%d %s%s" % (m, p[1], _plural(m)))
            n %= p[0]

    if not s:
        seconds = round(seconds * 10) / 10
        s.append("%g second%s" % (seconds, _plural(seconds)))
    return " ".join(s)


def big_number(value):
    return f"{value:,}"
