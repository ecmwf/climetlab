#!/usr/bin/env python
#
# (C) Copyright 2012- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#


import datetime
import itertools
from collections import defaultdict
from copy import copy
from functools import cmp_to_key

from dateutil.parser import parse as parse_dates


class Interval(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
        if not isinstance(start, datetime.date) and not isinstance(end, datetime.date):
            self.one = datetime.timedelta(hours=1)
            raise NotImplementedError("Interval with time not yet supported")
        else:
            self.one = datetime.timedelta(days=1)
        assert start <= end
        assert isinstance(start, datetime.date)
        assert isinstance(end, datetime.date)

    def count(self):
        return (self.end - self.start).days + 1

    def split(self, dates):
        result = []

        bounds = set(dates)
        bounds.discard(self.start)
        bounds.discard(self.end)

        s = self.start
        e = self.end
        for b in sorted(bounds):
            if b >= s and b <= e:
                result.append(self.__class__(s, b))
                s = b + self.one

        result.append(self.__class__(s, e))
        return result

    def overlaps(self, other):
        """Returns the union of two intervals if they overlap, else None"""
        s1, e1 = self.start, self.end + self.one
        s2, e2 = other.start, other.end + self.one
        s = max(s1, s2)
        e = min(e1, e2)
        if s <= e:
            return self.__class__(min(s1, s2), max(e1, e2) - self.one)
        else:
            return None

    def intersects(self, other):
        """Returns the intersection of two intervals if they overlap, else None"""
        s1, e1 = self.start, self.end + self.one
        s2, e2 = other.start, other.end + self.one
        s = max(s1, s2)
        e = min(e1, e2)
        if s <= e:
            return self.__class__(max(s1, s2), min(e1, e2) - self.one)
        else:
            return None

    @classmethod
    def expand(cls, lst):
        for i in lst:
            d = i.start
            while d <= i.end:
                yield d.date()
                d = d + datetime.timedelta(days=1)

    @classmethod
    def intersection(cls, list1, list2):
        result = []
        for i1 in list1:
            for i2 in list2:
                result.append(i1.intersects(i2))

        return Interval.join([r for r in result if r is not None])

    @classmethod
    def join(cls, intervals):
        result = sorted(intervals)

        more = True
        while more:
            more = False

            for i in range(len(result)):
                if result[i] is not None:
                    for j in range(i + 1, len(result)):
                        o = result[i].overlaps(result[j])
                        if o is not None:
                            result[i] = o
                            result[j] = None
                            more = True

            result = [r for r in result if r is not None]

        return tuple(result)

    def __repr__(self):
        if isinstance(self.start, datetime.date):

            if self.start == self.end:
                return self.start.strftime("%Y-%m-%d")

            return "%s/%s" % (
                self.start.strftime("%Y-%m-%d"),
                self.end.strftime("%Y-%m-%d"),
            )

        if self.start == self.end:
            return self.start.isoformat()
        return "%s/%s" % (self.start.isoformat(), self.end.isoformat())

    def __lt__(self, other):
        return (self.start, self.end) < (other.start, other.end)

    def __le__(self, other):
        return (self.start, self.end) <= (other.start, other.end)

    def __gt__(self, other):
        return (self.start, self.end) > (other.start, other.end)

    def __ge__(self, other):
        return (self.start, self.end) >= (other.start, other.end)

    def __eq__(self, other):
        return (self.start, self.end) == (other.start, other.end)

    def __ne__(self, other):
        return (self.start, self.end) != (other.start, other.end)

    def __hash__(self):
        return hash((self.start, self.end))


def _cleanup(x):

    if isinstance(x, (list, tuple)):
        return [_cleanup(a) for a in x]

    if isinstance(x, dict):
        return {_cleanup(k): _cleanup(v) for k, v in x.items()}

    if isinstance(x, (str, int, float)):
        return x

    return str(repr(x))


def _to_hashable(x):
    assert isinstance(x, dict)
    return tuple((k, v) for k, v in sorted(x.items()))


def _from_hashable(x):
    assert isinstance(x, tuple)
    return {k: v for k, v in x}


def _as_tuple(t):
    if isinstance(t, tuple):
        return t
    if isinstance(t, list) and len(t) == 1:
        return _as_tuple(t[0])
    if isinstance(t, (list, set)):
        return tuple(t)
    return (t,)


def _as_interval(interval):
    if not isinstance(interval, (list, tuple)):
        interval = [interval]
    result = []
    for t in interval:
        if isinstance(t, Interval):
            result.append(t)
            continue

        if isinstance(t, datetime.date):
            result.append(Interval(t, t))
            continue

        bits = t.split("/")
        assert len(bits) in (1, 2)
        if len(bits) == 1:
            start = end = bits[0]
        else:
            start = bits[0]
            end = bits[1]
        start = parse_dates(start)
        end = parse_dates(end)
        result.append(Interval(start, end))
    return result


class Tree:
    def __init__(self, values=None, intervals=None):
        self._values = {} if values is None else values
        self._children = []
        self._unique_values = None
        self._flatten = None
        self._intervals = set() if intervals is None else intervals

    def _add_child(self, child):
        self._children.append(child.compact())

    def _set_value(self, name, value):
        self._values[name] = value

    def _join_intervals(self, name):
        self._intervals.add(name)

        for c in self._children:
            c._join_intervals(name)

        if name in self._values:
            self._values[name] = Interval.join(self._values[name])

    def unique_values(self):
        if self._unique_values is None:
            u = self._unique_values = {}

            for r in self.flatten():
                for k, v in r.items():
                    u.setdefault(k, set())
                    for x in v:
                        u[k].add(x)

            for i in self._intervals:
                u[i] = Interval.join(u[i])

            for k in u.keys():
                u[k] = tuple(sorted(u[k]))

        return dict(**self._unique_values)

    def flatten(self):
        if self._flatten is None:
            self._flatten = tuple(self._flatten_tree())
        return self._flatten

    def _flatten_tree(self):
        if not self._children:
            yield self._values
        else:
            for c in self._children:
                for t in c._flatten_tree():
                    r = dict(**self._values)
                    r.update(t)
                    yield r

    def to_list(self):
        result = []
        for r in _cleanup(self.flatten()):
            s = {k: sorted(v) for k, v in sorted(r.items())}
            result.append(s)

        return sorted(result, key=lambda a: sorted(a.items()))

    def visit(self, visitor, depth=0):
        visitor(self._values, depth)
        for c in self._children:
            c.visit(visitor, depth + 1)

    def _kwargs_to_request(self, _kwargs=None, **kwargs):
        if _kwargs is not None and not kwargs:
            assert isinstance(_kwargs, dict)
            kwargs = _kwargs

        request = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            if k in self._intervals:
                request[k] = _as_interval(v)
            else:
                request[k] = _as_tuple(v)
        return request

    def count(self, _kwargs=None, **kwargs):

        return self._count(self._kwargs_to_request(_kwargs, **kwargs))

    def _count(self, request):

        if not self._values and not self._children:
            return 0

        ok, matches = self._match(request)
        if not ok:
            return 0

        r = dict(**self._values)
        for name, values in [(n, v) for (n, v) in matches.items() if n in self._values]:
            r[name] = _as_tuple(values)

        count = 1
        for name, values in r.items():
            if name in self._intervals:
                count *= sum(i.count() for i in values)
            else:
                count *= len(values)

        if not self._children:
            return count

        return sum(count * c._count(request) for c in self._children)

    def select(self, **kwargs):
        result = self._select(self._kwargs_to_request(**kwargs))
        if result is None:
            return Tree()
        return result.factorise()

    def _select(self, request):
        ok, matches = self._match(request)
        if not ok:
            return None

        r = dict(**self._values)
        for name, values in [(n, v) for (n, v) in matches.items() if n in self._values]:
            r[name] = _as_tuple(values)
        result = Tree(r, self._intervals)

        if not self._children:
            return result

        cnt = 0
        for c in self._children:
            s = c._select(request)
            if s is not None:
                cnt += 1
                result._add_child(s)

        if cnt == 0:
            return None

        return result

    def missing(self, **kwargs):
        request = self._kwargs_to_request(**kwargs)
        user = {_to_hashable(x) for x in self._iterate_request(request)}
        tree = {_to_hashable(x) for x in self.iterate(True)}

        s = [_from_hashable(x) for x in user.difference(user.intersection(tree))]

        return _factorise(s, intervals=self._intervals)

    def _match(self, request):
        matches = {}
        for name, values in [(n, v) for (n, v) in request.items() if n in self._values]:

            if name in self._intervals:
                common = Interval.intersection(values, self._values[name])
            else:
                common = set(values).intersection(set(self._values[name]))

            if len(common) == 0:
                return False, None

            if False:  # If we want an exact match
                if len(common) != len(values):
                    return False, None

            matches[name] = common

        return True, matches

    def iterate(self, expand=False):
        for r in self._flatten_tree():
            if expand:
                yield from self._iterate_request(r)
            else:
                yield r

    def _iterate_request(self, r):
        for name in self._intervals:
            r[name] = Interval.expand(r[name])
        yield from (dict(zip(r.keys(), x)) for x in itertools.product(*r.values()))

    def compact(self):
        if not self._values and len(self._children) == 1:
            return self._children[0]
        return self

    def factorise(self):
        return _factorise(list(self._flatten_tree()), intervals=self._intervals)

    def as_mars(self, verb="retrieve", extra=None):
        result = []
        for r in self.flatten():
            req = [verb]
            if extra is not None:
                req.append(extra)
            for k, v in r.items():
                req.append(f"{k}={'/'.join(v)}")
            result.append(",".join(req))
        return "\n".join(result)

    def as_mars_list(self):

        text = []
        indent = {}
        order = {}

        def V(request, depth):
            if not request:
                return

            if depth not in indent:
                indent[depth] = len(indent)

            text.append(" " * indent[depth])

            for k in sorted(request.keys()):
                if k not in order:
                    order[k] = len(order)

            sep = ""
            for k, v in sorted(request.items(), key=lambda x: order[x[0]]):
                text.append(sep)
                text.append(k)
                text.append("=")

                if isinstance(v[0], Interval):
                    v = [str(x) for x in v]

                if len(v) == 1:
                    text.append(v[0])
                else:
                    text.append("/".join(sorted(str(x) for x in v)))
                sep = ","
            text.append("\n")

        self.visit(V)

        return "".join(str(x) for x in text)

    def tree(self):

        text = []
        indent = {}
        order = {}

        def V(request, depth):
            if not request:
                return

            if depth not in indent:
                indent[depth] = len(indent) * 3

            text.append(" " * indent[depth])

            for k in sorted(request.keys()):
                if k not in order:
                    order[k] = len(order)

            sep = ""
            for k, v in sorted(request.items(), key=lambda x: order[x[0]]):
                text.append(sep)
                text.append(k)
                text.append("=")

                if isinstance(v[0], Interval):
                    v = [str(x) for x in v]

                if len(v) == 1:
                    text.append(v[0])
                else:
                    text.append("[")
                    text.append(", ".join(sorted(str(x) for x in v)))
                    text.append("]")
                sep = ", "
            text.append("\n")

        self.visit(V)

        return "".join(str(x) for x in text)


class Column(object):
    """Just what is says on the tin, a column of values."""

    def __init__(self, title, values):
        self.title = title
        self.values = values
        self.prio = 0
        self.diff = -1

    def __lt__(self, other):
        return (self.prio, self.diff, self.title) < (
            other.prio,
            other.diff,
            other.title,
        )

    def value(self, i):
        return self.values[i]

    def set_value(self, i, v):
        self.values[i] = v

    def compute_differences(self, idx):
        """
        Number of unique values in this column for the requested
        row indexes.

        @param idx list of row indexes
        """
        x = [self.values[i] for i in idx]
        try:
            self.diff = len(set(x))
        except Exception:
            print(type(x))
            print(x[:10])
            raise

    def __repr__(self):
        return "Column(%s,%s,%s,%s)" % (self.title, self.values, self.prio, self.diff)


class Table(object):
    def __init__(self, other=None, a=None, b=None):

        self.tree = Tree()

        if other is not None:
            self.depth = other.depth + 1
            self.cols = copy(other.cols)
            self.colidx = copy(other.colidx)
            self.rowidx = other.rowidx[a:b]
        else:
            self.depth = 0
            self.cols = []
            self.colidx = []
            self.rowidx = []

    def get_elem(self, c, r):
        return self.cols[self.colidx[c]].value(self.rowidx[r])

    def set_elem(self, c, r, v):
        return self.cols[self.colidx[c]].set_value(self.rowidx[r], v)

    def __repr__(self):
        return repr(
            [[self.cols[col].value(row) for row in self.rowidx] for col in self.colidx]
        )

    def column(self, s, col):
        self.cols.append(Column(s, col))
        self.colidx.append(len(self.colidx))

        if len(col) > len(self.rowidx):
            self.rowidx = [i for i in range(len(col))]

    def one_less(self, r, n):
        return [self.get_elem(i, r) for i in range(len(self.colidx)) if i != n]

    def factorise1(self):
        self.pop_singles()
        self.sort_rows()

        for i in range(len(self.colidx)):
            self.factorise2(len(self.colidx) - i - 1)

    def factorise2(self, n):
        remap = defaultdict(list)
        gone = []

        for i in range(len(self.rowidx)):
            v = self.one_less(i, n)
            s = remap[_as_tuple(v)]
            if len(s) != 0:
                gone.append(i)
            elem = self.get_elem(n, i)
            if elem not in s:
                s.append(elem)

        for g in reversed(gone):
            del self.rowidx[g]

        for i in range(len(self.rowidx)):
            v = self.one_less(i, n)
            s = remap[_as_tuple(v)]
            self.set_elem(n, i, _as_tuple(s))

    def sort_columns(self):
        """
        Sort the columns on the number of unique values (this column.diff).
        """
        for idx in self.colidx:
            self.cols[idx].compute_differences(self.rowidx)

        self.colidx.sort(key=lambda a: self.cols[a])

    def compare_rows(self, a, b):
        for idx in self.colidx:
            sa = self.cols[idx].value(a)
            sb = self.cols[idx].value(b)

            if sa is None and sb is None:
                continue

            if sa < sb:
                return -1

            if sa > sb:
                return 1

        return 0

    def sort_rows(self):
        self.rowidx.sort(key=cmp_to_key(self.compare_rows))

    def pop_singles(self):
        """
        Take the column with just one unique value and add them to the
        tree. Delete their index from the list of column indexes.
        """
        self.sort_columns()
        ok = False
        while len(self.colidx) > 0 and self.cols[self.colidx[0]].diff == 1:
            s = _as_tuple(self.get_elem(0, 0))
            self.tree._set_value(self.cols[self.colidx[0]].title, s)
            del self.colidx[0]
            ok = True

        return ok

    def split(self):
        if len(self.rowidx) < 2 or len(self.colidx) < 2:
            return

        self.sort_columns()
        self.sort_rows()

        prev = self.get_elem(0, 0)
        j = 0

        for i in range(1, len(self.rowidx)):
            e = self.get_elem(0, i)
            if prev != e:
                table = Table(self, j, i)
                self.tree._add_child(table.process())
                j = i
                prev = e

        if j > 0:
            table = Table(self, j, len(self.rowidx))
            self.tree._add_child(table.process())
            self.rowidx = []

    def process(self):
        self.factorise1()
        self.pop_singles()
        self.split()
        return self.tree


def _scan(r, cols, name, rest):
    """Generate all possible combinations of values. Each set of values is
    stored in a list and each value is repeated as many times so that if taking
    one row in all value lists, I will get one unique combination of values
    between all input keys.

    @param r    request as a dict
    @param cols actual result of the _scan
    @param name current request key we are processing
    @param rest remaining request keys to process
    """
    n = 0
    # print("Scan", name)
    c = cols[name]
    for value in r.get(name, ["-"]):
        m = 1
        if rest:
            m = _scan(r, cols, rest[0], rest[1:])
        for _ in range(m):
            c.append(value)
        n += m

    return n


def _as_requests(r):

    s = {}
    for k, v in r.items():
        if not isinstance(v, (tuple, list)):
            s[k] = [v]
        else:
            s[k] = v

    return s


def factorise(req, *, intervals=None):
    # Make a copy so we don't modify the original
    safe = [dict(**r) for r in req]
    return _factorise(safe, intervals=intervals)


def _factorise(req, intervals=None):

    if intervals is None:
        intervals = []

    if not isinstance(intervals, (list, tuple, set)):
        intervals = [intervals]

    if intervals:
        for r in req:
            for i in intervals:
                if i in r:
                    r[i] = _as_interval(r[i])

    for i in intervals:
        # Collect all dates
        dates = set()
        for r in req:
            for interval in r.get(i, []):
                dates.add(interval.start)
                dates.add(interval.end)

        # Split intervals according to collected dates
        for r in req:
            if i in r:
                splits = []
                for interval in r.get(i, []):
                    splits.extend(interval.split(dates))
                r[i] = splits

    req = [_as_requests(r) for r in req]

    names = list({name for r in req for name in r.keys()})

    cols = defaultdict(list)
    if names:
        for r in req:
            _scan(r, cols, names[0], names[1:])

    table = Table()
    for n, c in cols.items():
        table.column(n, c)

    tree = table.process()

    for i in intervals:
        tree._join_intervals(i)

    return tree.compact()
