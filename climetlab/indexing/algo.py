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


def optimal_split(url, parts, download_cost=1.0, split_cost=3.0):
    # download_cost:
    #    unit is seconds/megabyte.
    #    additional cost to download one useles byte.
    # split_cost:
    #    unit is microseconds.
    #    additional cost to do one additional HTTP request.

    if len(parts) == 0:
        return [parts]

    _parts = [parts[0]]
    holes = []

    for offset, length in parts[1:]:
        latest = _parts[-1]
        latest_end = latest[0] + latest[1]

        distance = offset - latest_end
        assert distance >= 0, (distance, latest, (offset, length), parts, url)

        # if distance == 0: # adjacents: merge immediately
        #    _parts[-1] = [latest[0], latest[1] + length]
        #    continue

        cost_of_merging = distance * download_cost - split_cost
        # print(cost_of_merging, distance* download_cost, split_cost)

        if cost_of_merging <= 0:
            # print('merging')
            _parts[-1] = [latest[0], latest[1] + length]
        else:
            _parts.append([offset, length])

        holes.append((distance, latest_end))  # TODO: check -/+ 1

    return [_parts]


SPLIT_FUNCTIONS = {
    "minimum-split": minimum_split,
    "maximum-split": maximum_split,
    "optimal-split": optimal_split,
}


def resplit_urls_parts(dic_urls_parts, method="minimum-split"):
    dic_urls_parts = {k: sorted(v) for k, v in dic_urls_parts.items()}

    split_func = SPLIT_FUNCTIONS[method]

    better = []
    for url, parts in dic_urls_parts.items():
        for _parts in split_func(url, parts):
            better.append((url, _parts))
    return better
