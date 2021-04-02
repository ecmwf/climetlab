# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import datetime


class IntHelper:
    def __init__(self, data):
        self.data = data

    def to_datetime(self):
        if self.data <= 0:
            date = datetime.datetime.utcnow() + datetime.timedelta(days=self.data)
            return datetime.datetime(date.year, date.month, date.day)
        else:
            return datetime.datetime(
                self.data // 10000, self.data % 10000 // 100, self.data % 100
            )

    def to_datetime_list(self):
        return [self.to_datetime()]


def helper(data, *args, **kwargs):
    if isinstance(data, int):
        return IntHelper(data)
    return None
