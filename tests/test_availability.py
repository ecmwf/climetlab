#!/usr/bin/env python3

# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import pandas as pd
import pytest
import yaml

from climetlab.decorators import availability
from climetlab.utils.availability import Availability


@pytest.fixture
def availability_s2s_1():
    s2s_config = """
    ecmwf:
        param: ['2t', 'ci', 'gh', 'lsm', 'msl']
        number: 50
        alldates: {start: '2020-01-02', end: '2020-12-31', freq: 'w-thu'}
    eccc:
        param: ['2t', 'ci', 'gh', 'lsm']
        number: 20
        alldates: {start: '2020-01-02', end: '2020-12-31', freq: 'w-thu'}
    ncep:
        param: ['2t', 'ci', 'gh']
        number: 15
        alldates: {start: '2010-01-02', end: '2010-12-31', freq: 'w-thu'}
    """

    config = yaml.safe_load(s2s_config)

    availability_list = []

    for k, v in config.items():
        dic = dict(origin=k)
        dic["date"] = [x.strftime("%Y-%m-%d") for x in pd.date_range(**v["alldates"])][
            :3
        ]
        dic["number"] = list(range(1, v["number"] + 1))
        dic["param"] = v["param"][:3]
        availability_list.append(dic)
    av = Availability(availability_list)
    return av


def parser(v):
    # import pandas as pd

    if "alldates" in v:
        v["alldates"] = v["alldates"]["start"] + "/" + v["alldates"]["end"]
        # not using: v["alldates"]['freq']
        # but this does not work:
        # v["alldates"] = list(pd.date_range(**v["alldates"]))
        v["date"] = v.pop("alldates")

    if "number" in v:
        s, _, e = v["number"].split("/")
        v["number"] = [x for x in range(int(s), int(e) + 1)]

    for remove in [
        "grid",
        "stream",
        "step",
        "stepintervals",
        "level",
        "levelbis",
    ]:
        v.pop(remove, None)

    return v


C0 = [
    {"level": "500", "param": "Z", "step": "24"},
    {"level": "500", "param": "Z", "step": "36"},
    {"level": "500", "param": "Z", "step": "48"},
    {"level": "500", "param": "T", "step": "24"},
    {"level": "500", "param": "T", "step": "36"},
    {"level": "500", "param": "T", "step": "48"},
    {"level": "850", "param": "T", "step": "36"},
    {"level": "850", "param": "T", "step": "48"},
    {"level": "1000", "param": "Z", "step": "24"},
    {"level": "1000", "param": "Z", "step": "48"},
]

C1 = [
    {"level": "500", "param": "a", "step": "24"},
    {"level": "500", "param": "a", "step": "36"},
    {"level": "500", "param": "a", "step": "48"},
    {"level": "500", "param": "b", "step": "24"},
    {"level": "500", "param": "b", "step": "36"},
    {"level": "500", "param": "b", "step": "48"},
    {"level": "850", "param": "b", "step": "36"},
    {"level": "850", "param": "b", "step": "48"},
    {"level": "1000", "param": "a", "step": "24"},
    {"level": "1000", "param": "a", "step": "48"},
]


@availability(C0)
def func1(level, param, step):
    pass


def test_availability_1():
    func1(level="1000", param="Z", step="24")
    with pytest.raises(ValueError):
        func1(level="1032100", param="Z", step="24")


@availability("availability.json")
def func2(level, param, step):
    pass


def test_availability_2():
    func2("1000", "Z", "24")


def test_availability_3():
    avail = Availability(C0)
    print(avail)


def test_s2s(availability_s2s_1):
    av = availability_s2s_1

    print(av.tree())

    with pytest.raises(ValueError):
        av.check(number=75)
    av.check(number=7)

    av.check(number=30, origin="ecmwf")
    with pytest.raises(ValueError):
        av.check(number=30, origin="eccc")

    #   av.check(origin='ncep')
    for i in av.flatten():
        print(i)
    # av.check(origin=["unknown"])
    print(av.tree())

    #    av.check(number=1, date=["2010-01-07","2010-01-14"])
    #    av.check(number=1, date=["2010-01-07","2010-01-14"], origin=["unknown"])
    #    av.check(number=1, date=["2010-01-02","2010-01-09"], origin=["ecmwf", "eccc"])

    print("...")
    print(
        av.missing(
            number=1,
            origin=["ecmwf", "ncep"],
            date="2020-01-09",
            # param=['2t', 'ci'],
        ).tree()
    )
    print(
        av.count(
            number=1,
            origin=["ecmwf", "ncep"],
            date="2020-01-09",
        )
    )


@pytest.fixture
def availability_s2s_2():
    s2s_bis = """
    - origin: ecmwf
      fctype: hindcast
      param: ['2t', 'ci', 'gh', 'lsm', 'msl', 'q', 'rsn', 'sm100', 'sm20', 'sp', 'sst', 'st100', 'st20', 't', 'tcc', 'tcw', 'tp', 'ttr', 'u', 'v']
      number: 1/to/50
      stream: enfh
      step: 0/to/1104/by/24
      stepintervals: 0-24/24-48/48-72/72-96/96-120/120-144/144-168/168-192/192-216/216-240/240-264/264-288/288-312/312-336/336-360/360-384/384-408/408-432/432-456/456-480/480-504/504-528/528-552/552-576/576-600/600-624/624-648/648-672/672-696/696-720/720-744/744-768/768-792/792-816/816-840/840-864/864-888/888-912/912-936/936-960/960-984/984-1008/1008-1032/1032-1056/1056-1080/1080-1104
      levels: 1000/925/850/700/500/300/200/100/50/10
      levelsbis: 1000/925/850/700/300/500/200
      grid: null
      hdate: ALL
      alldates: {start: '2020-01-02', end: '2020-12-31', freq: 'w-thu'}

    - origin: eccc
      fctype: hindcast
      param: ['2t', 'ci', 'gh', 'lsm', 'msl', 'q', 'rsn', 'sp', 'sst', 't', 'tcc', 'tcw', 'tp', 'ttr', 'u', 'v']
      number: 1/to/50
      stream: enfh
      step: 24/to/768/by/24
      stepintervals: 0-24/24-48/48-72/72-96/96-120/120-144/144-168/168-192/192-216/216-240/240-264/264-288/288-312/312-336/336-360/360-384/384-408/408-432/432-456/456-480/480-504/504-528/528-552/552-576/576-600/600-624/624-648/648-672/672-696/696-720/720-744/744-768
      levels: 1000/925/850/700/500/300/200/100/50/10
      levelsbis: 1000/925/850/700/300/500/200
      grid: null
      hdate: ALL
      alldates: {start: '2020-01-02', end: '2020-12-31', freq: 'w-thu'}

    # ncep hindcast has run only once, with date = 2011-03-01
    - origin: ncep
      fctype: hindcast
      param: ['2t', 'ci', 'gh', 'lsm', 'msl', 'q', 'sm100', 'sm20', 'sp', 'sst', 'st100', 'st20', 't', 'tcc', 'tcw', 'tp', 'ttr', 'u', 'v']
      number: 1/to/3
      stream: enfh
      step: 24/to/1056/by/24
      stepintervals: 24-48/48-72/72-96/96-120/120-144/144-168/168-192/192-216/216-240/240-264/264-288/288-312/312-336/336-360/360-384/384-408/408-432/432-456/456-480/480-504/504-528/528-552/552-576/576-600/600-624/624-648/648-672/672-696/696-720/720-744/744-768/768-792/792-816/816-840/840-864/864-888/888-912/912-936/936-960/960-984/984-1008/1008-1032/1032-1056
      levels: 1000/925/850/700/500/300/200/100/50/10
      levelsbis: 1000/925/850/700/300/500/200
      grid: null
      # note that this is 2010, that is why the date for ncep is not starting on 2010-01-02 (which is not a thursday btw)
      alldates: {start: '2010-01-07', end: '2010-12-29', freq: 'w-thu'}
    """  # noqa: E501

    av = Availability(
        s2s_bis,
        parser=parser,
        intervals="date",
    )
    return av


def test_availability_4(availability_s2s_2):
    av = availability_s2s_2
    av.check(number=30, origin="eccc")
    with pytest.raises(ValueError):
        av.check(number=100, fctype="hindcast", origin="ecmwf")
    av.check(number=30, date="2020-01-02", origin="eccc")
    with pytest.raises(ValueError):
        av.check(number=30, date="2111-01-02", origin="eccc")

    # this should raise a ValueError
    # with pytest.raises(ValueError):
    #     av.check(number=30, alldates='2020-01-03', origin="eccc")


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
