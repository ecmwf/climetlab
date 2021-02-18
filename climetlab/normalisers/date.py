# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.utils.dates import to_date_list


class DateListNormaliser:
    def __init__(self, format=None):
        self.format = format

    def normalise(self, dates):
        dates = to_date_list(dates)
        if self.format is not None:
            dates = [d.strftime(self.format) for d in dates]
        return dates
