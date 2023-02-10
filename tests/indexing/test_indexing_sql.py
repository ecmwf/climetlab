#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import pytest
import sys

from climetlab.core.temporary import temp_file
from climetlab.indexing.database.json import JsonDatabase
from climetlab.indexing.database.sql import SqlDatabase


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="file:// not working on Windows yet",
)
@pytest.mark.parametrize("cls", (SqlDatabase, JsonDatabase))
def test_load(cls):
    lst = [
        {
            "_path": "data/01.grb",
            "param": "z",
            "domain": "g",
            "levtype": "pl",
            "levelist": "500",
            "date": "19970101",
            "time": "0000",
            "step": "0",
            "class": "ea",
            "type": "an",
            "stream": "oper",
            "expver": "0001",
            "_offset": 0,
            "_length": 23358,
        },
        {
            "_path": "data/01.grb",
            "param": "z",
            "domain": "g",
            "levtype": "pl",
            "levelist": "500",
            "date": "19970101",
            "time": "0100",
            "step": "0",
            "class": "ea",
            "type": "an",
            "stream": "oper",
            "expver": "0001",
            "_offset": 23358,
            "_length": 23358,
        },
        {
            "_path": "data/01.grb",
            "param": "z",
            "domain": "g",
            "levtype": "pl",
            "levelist": "500",
            "date": "19970101",
            "time": "0200",
            "step": "0",
            "class": "ea",
            "type": "an",
            "stream": "oper",
            "expver": "0001",
            "_offset": 46716,
            "_length": 23358,
        },
        {
            "_path": "data/01.grb",
            "param": "z",
            "domain": "g",
            "levtype": "pl",
            "levelist": "500",
            "date": "19970101",
            "time": "0300",
            "step": "0",
            "class": "ea",
            "type": "an",
            "stream": "oper",
            "expver": "0001",
            "_offset": 70074,
            "_length": 23358,
        },
        {
            "_path": "data/02.grb",
            "param": "r",
            "domain": "g",
            "levtype": "pl",
            "levelist": "850",
            "date": "19970228",
            "time": "2300",
            "step": "0",
            "class": "ea",
            "type": "an",
            "stream": "oper",
            "expver": "0001",
            "_offset": 94156098,
            "_length": 23358,
        },
    ]
    # TmpDirectory()
    with temp_file(extension=".db") as db_path:
        db = cls(db_path)
        db.load(lst)
        for i, dic in enumerate(db.lookup_dicts()):
            assert len(dic) == len(lst[i])
            for k, v in dic.items():
                assert lst[i][k] == v

        for i, part in enumerate(db.lookup_parts()):
            assert part.path.endswith(lst[i]["_path"])
            assert part.length == lst[i]["_length"]
            assert part.offset == lst[i]["_offset"]


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
    # test_load(SqlDatabase)
