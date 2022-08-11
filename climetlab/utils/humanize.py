# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import re
from collections import defaultdict


def bytes(n):
    u = ["", " KiB", " MiB", " GiB", " TiB", " PiB", "EiB", "ZiB", "YiB"]
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


def seconds(seconds):

    if isinstance(seconds, datetime.timedelta):
        seconds = seconds.total_seconds()

    if seconds == 0:
        return "instantaneous"

    if seconds < 0.1:
        units = [
            None,
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


def number(value):
    return f"{value:,}"


def plural(value, what):
    return f"{number(value)} {what}{_plural(value)}"


DOW = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

MONTH = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def __(n):
    if n in (11, 12, 13):
        return "th"

    if n % 10 == 1:
        return "st"

    if n % 10 == 2:
        return "nd"

    if n % 10 == 3:
        return "rd"

    return "th"


def when(then, now=None, short=True):
    last = "last"

    if now is None:
        now = datetime.datetime.now()

    diff = (now - then).total_seconds()

    if diff < 0:
        last = "next"
        diff = -diff

    diff = int(diff)

    if diff == 0:
        return "right now"

    def _(x):
        if last == "last":
            return "%s ago" % (x,)
        else:
            return "in %s" % (x,)

    if diff < 60:
        diff = int(diff + 0.5)
        return _("%s second%s" % (diff, _plural(diff)))

    if diff < 60 * 60:
        diff /= 60
        diff = int(diff + 0.5)
        return _("%s minute%s" % (diff, _plural(diff)))

    if diff < 60 * 60 * 6:
        diff /= 60 * 60
        diff = int(diff + 0.5)
        return _("%s hour%s" % (diff, _plural(diff)))

    jnow = now.toordinal()
    jthen = then.toordinal()

    if jnow == jthen:
        return "today at %02d:%02d" % (then.hour, then.minute)

    if jnow == jthen + 1:
        return "yesterday at %02d:%02d" % (then.hour, then.minute)

    if jnow == jthen - 1:
        return "tomorrow at %02d:%02d" % (then.hour, then.minute)

    if abs(jnow - jthen) <= 7:
        return "%s %s" % (
            last,
            DOW[then.weekday()],
        )

    if abs(jnow - jthen) < 32 and now.month == then.month:
        return "the %d%s of this month" % (then.day, __(then.day))

    if abs(jnow - jthen) < 64 and now.month == then.month + 1:
        return "the %d%s of %s month" % (then.day, __(then.day), last)

    if short:
        years = int(abs(jnow - jthen) / 365.25 + 0.5)
        if years == 1:
            return "%s year" % last

        if years > 1:
            return _("%d years" % (years,))

        month = then.month
        if now.year != then.year:
            month -= 12

        d = abs(now.month - month)
        if d >= 12:
            return _("a year")
        else:
            return _("%d month%s" % (d, _plural(d)))

    return "on %s %d %s %d" % (
        DOW[then.weekday()],
        then.day,
        MONTH[then.month],
        then.year,
    )


def string_distance(s, t):
    import numpy as np

    m = len(s)
    n = len(t)
    d = np.zeros((m + 1, n + 1), dtype=int)

    one = int(1)
    zero = int(0)

    d[:, 0] = np.arange(m + 1)
    d[0, :] = np.arange(n + 1)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = zero if s[i - 1] == t[j - 1] else one
            d[i, j] = min(
                d[i - 1, j] + one,
                d[i, j - 1] + one,
                d[i - 1, j - 1] + cost,
            )

    return d[m, n]


def did_you_mean(word, vocabulary):

    distance, best = min((string_distance(word, w), w) for w in vocabulary)
    # if distance < min(len(word), len(best)):
    return best


def dict_to_human(query):

    lst = [f"{k}={v}" for k, v in sorted(query.items())]

    return list_to_human(lst)


def list_to_human(lst):
    if not lst:
        return "??"

    if len(lst) > 2:
        lst = [", ".join(lst[:-1]), lst[-1]]

    return " and ".join(lst)


def as_number(value, name, units, none_ok):
    if value is None and none_ok:
        return None

    value = str(value)
    # TODO: support floats
    m = re.search(r"^\s*(\d+)\s*([%\w]+)?\s*$", value)
    if m is None:
        raise ValueError(f"{name}: invalid number/unit {value}")
    value = int(m.group(1))
    if m.group(2) is None:
        return value
    unit = m.group(2)[0]
    if unit not in units:
        valid = ", ".join(units.keys())
        raise ValueError(f"{name}: invalid unit '{unit}', valid values are {valid}")
    return value * units[unit]


def as_seconds(value, name=None, none_ok=False):
    units = dict(s=1, m=60, h=3600, d=86400, w=86400 * 7)
    return as_number(value, name, units, none_ok)


def as_percent(value, name=None, none_ok=False):
    units = {"%": 1}
    return as_number(value, name, units, none_ok)


def as_bytes(value, name=None, none_ok=False):
    units = {}
    n = 1
    for u in "KMGTP":
        n *= 1024
        units[u] = n
        units[u.lower()] = n

    return as_number(value, name, units, none_ok)


def as_timedelta(value, name=None, none_ok=False):
    if value is None and none_ok:
        return None

    save = value
    value = re.sub(r"[^a-zA-Z0-9]", "", value.lower())
    value = re.sub(r"([a-zA-Z])[a-zA-Z]*", r"\1", value)
    # value = re.sub(r"[^dmhsw0-9]", "", value)
    bits = [b for b in re.split(r"([dmhsw])", value) if b != ""]

    times = defaultdict(int)

    val = None

    for i, n in enumerate(bits):
        if i % 2 == 0:
            val = int(n)
        else:
            assert n in ("d", "m", "h", "s", "w")
            times[n] = val
            val = None

    if val is not None:
        if name:
            raise ValueError(f"{name}: invalid period '{save}'")
        raise ValueError(f"Invalid period '{save}'")

    return datetime.timedelta(
        weeks=times["w"],
        days=times["d"],
        hours=times["h"],
        minutes=times["m"],
        seconds=times["s"],
    )


def rounded_datetime(d):
    if float(d.microsecond) / 1000.0 / 1000.0 >= 0.5:
        d = d + datetime.timedelta(seconds=1)
    d = d.replace(microsecond=0)
    return d
