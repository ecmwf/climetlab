# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import datetime
import json
import logging
import warnings

LOG = logging.getLogger(__name__)


def json_serialiser(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


class DbKey:
    sql_type = "TEXT"
    type = str
    prefix = None

    def __init__(self, name):
        self.name = name
        assert self.prefix is not None

    @property
    def name_in_db(self):
        return self.prefix + "_" + self.name

    def normalize(self, value, db):
        return db.normalize_str(value)

    def to_sql_value(self, value):
        return "'" + str(value) + "'"


#
class CfgribDbKey(DbKey):
    type = str
    prefix = "c"


#
class FilepartKey(DbKey):
    prefix = ""

    def __init__(self, name):
        assert name[0] == "_", name
        super().__init__(name)

    @property
    def name_in_db(self):
        return self.name[1:]


class StrFilepartKey(FilepartKey):
    pass


class IntFilepartKey(FilepartKey):
    sql_type = "INTEGER"
    type = int

    def normalize(self, value, db):
        return db.normalize_int(value)

    def to_sql_value(self, value):
        return str(value)


#
class StatisticsDbKey(DbKey):
    prefix = "s"
    sql_type = "FLOAT"
    type = float

    def normalize(self, value, db):
        return db.normalize_float(value)

    def to_sql_value(self, value):
        return str(value)


#
class GribDbKey(DbKey):
    prefix = "i"


class StrGribKey(GribDbKey):
    pass


class IntGribKey(GribDbKey):
    sql_type = "INTEGER"
    type = int

    def normalize(self, value, db):
        return db.normalize_int(value)

    def to_sql_value(self, value):
        return str(value)


class IntIntervalGribKey(StrGribKey):
    # keep step as str because we can have intervals
    pass


class DatetimeGribKey(GribDbKey):
    sql_type = "TEXT"  # Change to INTEGER ?
    type = str

    def normalize(self, value, db):
        return db.normalize_datetime(value)

    def to_sql_value(self, value):
        return self.normalize(value)


GRIB_KEYS = [
    StrGribKey("class"),
    StrGribKey("stream"),
    StrGribKey("levtype"),
    StrGribKey("type"),
    StrGribKey("expver"),
    IntGribKey("date"),
    StrGribKey("hdate"),
    StrGribKey("andate"),
    IntGribKey("time"),
    StrGribKey("antime"),
    StrGribKey("reference"),
    IntIntervalGribKey("step"),
    StrGribKey("anoffset"),
    StrGribKey("verify"),
    StrGribKey("fcmonth"),
    StrGribKey("fcperiod"),
    IntGribKey("leadtime"),
    StrGribKey("opttime"),
    StrGribKey("origin"),
    StrGribKey("domain"),
    StrGribKey("method"),
    StrGribKey("diagnostic"),
    StrGribKey("iteration"),
    IntGribKey("number"),
    StrGribKey("quantile"),
    IntGribKey("levelist"),
    # "latitude"  # in the MARS vocabulary but not used.
    # "longitude"  # in the MARS vocabulary but not used.
    StrGribKey("range"),
    StrGribKey("param"),
    StrGribKey("ident"),
    StrGribKey("obstype"),
    StrGribKey("instrument"),
    StrGribKey("reportype"),
    StrGribKey("frequency"),  # for 2-d wave-spectra products
    StrGribKey("direction"),  # for 2-d wave-spectra products
    StrGribKey("channel"),  # for ea and ef
    #
    #
    StrGribKey("param_level"),
    DatetimeGribKey("valid"),
]
GRIB_KEYS_NAMES = [k.name for k in GRIB_KEYS]

STATISTICS_KEYS = [StatisticsDbKey(k) for k in ["mean", "std", "min", "max"]]
STATISTICS_KEYS_NAMES = [k.name for k in STATISTICS_KEYS]

CFGRIB_KEYS = [CfgribDbKey("md5_grid_section"), CfgribDbKey("_param_id")]
CFGRIB_KEYS_NAMES = [k.name for k in CFGRIB_KEYS]

FILEPARTS_KEYS = [
    StrFilepartKey("_path"),
    IntFilepartKey("_offset"),
    IntFilepartKey("_length"),
]

ALL_KEYS = FILEPARTS_KEYS + GRIB_KEYS + STATISTICS_KEYS + CFGRIB_KEYS
ALL_KEYS_DICT = {k.name: k for k in ALL_KEYS}


class Database:
    def lookup_parts(self):
        raise NotImplementedError("")

    def lookup_dicts(self, *args, **kwargs):
        raise NotImplementedError("")

    def lookup_json_dicts(self, *args, **kwargs):
        for dic in self.lookup_dicts(*args, **kwargs):
            yield json.dumps(dic, default=json_serialiser)

    def count(self, request):
        raise NotImplementedError("")

    def load(self, iterator):
        raise NotImplementedError("")

    def sel(self, selection):
        raise NotImplementedError("")

    def order_by(self, order):
        raise NotImplementedError("")

    # serialisations
    def normalize(self, entry):
        e = dict()
        for k, v in entry.items():
            key = ALL_KEYS_DICT.get(k, None)
            if key is None:
                warnings.warn(f"{__file__}: ignoring unknown key {k}")
                continue
            e[k] = key.normalize(v, db=self)
        return e

    def normalize_datetime(self, value):
        raise NotImplementedError("")

    def normalize_float(self, value):
        return float(value)

    def normalize_int(self, value):
        return int(value)

    def normalize_str(self, value):
        return str(value)
