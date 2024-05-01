# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import datetime

from climetlab.wrappers import Wrapper


class DateWrapper(Wrapper):
    def __init__(self, data):
        self.data = data

    def to_datetime(self):
        return datetime.datetime(self.data.year, self.data.month, self.data.day)

    def to_datetime_list(self):
        return [self.to_datetime()]


def wrapper(data, *args, **kwargs):
    if isinstance(data, datetime.date):
        return DateWrapper(data)
    return None
