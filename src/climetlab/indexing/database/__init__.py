# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

LOG = logging.getLogger(__name__)


FILEPARTS_KEY_NAMES = ["_path", "_offset", "_length"]
STATISTICS_KEY_NAMES = ["mean", "std", "min", "max", "shape"]
MORE_KEY_NAMES_WITH_UNDERSCORE = ["_param_id"]
MORE_KEY_NAMES = ["datetime", "param_level"]


class DBKey:
    cast = None

    def __init__(self, name):
        self.name = name


class StrDBKey(DBKey):
    sql_type = "TEXT"
    cast = str


class FloatDBKey(DBKey):
    sql_type = "FLOAT"
    cast = float


class IntDBKey(DBKey):
    sql_type = "INTEGER"
    cast = int


# class
# stream
# levtype
# type
# expver
# date
# hdate
# andate
# time
# antime
# reference
# ribKey(
# anoffset
# verify
# fcmonth
# fcperiod
# leadtime
# opttime
# origin
# domain
# method
# diagnostic
# iteration
# number
# quantile
# levelist
#   # in the MARS vocabulary but not used.
#
# range
# param
# ident
# obstype
# instrument
# reportype
# frequency
# direction
# channel
#
# param_level
# Key(


class Database:
    def lookup_parts(self):
        raise NotImplementedError("")

    def lookup_dicts(self, *args, **kwargs):
        raise NotImplementedError("")

    def count(self, request):
        raise NotImplementedError("")

    def load_iterator(self, iterator):
        raise NotImplementedError("")

    def sel(self, selection):
        raise NotImplementedError("")

    def order_by(self, order):
        raise NotImplementedError("")

    def already_loaded(self, path_or_url, owner):
        return False
