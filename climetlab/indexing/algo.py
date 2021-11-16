# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
def minimum_split(url, parts):
    return [parts]


def maximum_split(url, parts):
    return [[p] for p in parts]


def optimal_split(url, parts):
    # TODO
    return [parts]


def resplit_urls_parts(dic_urls_parts, method="minimum-split"):
    better = []
    split_func = {
        "minimum-split": minimum_split,
        "maximum-split": maximum_split,
        "optimal": optimal_split,
    }[method]
    for url, parts in dic_urls_parts.items():
        for _parts in split_func(url, parts):
            better.append((url, _parts))
    return better
