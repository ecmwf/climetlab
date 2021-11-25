# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import re
from collections import namedtuple

LOG = logging.getLogger(__name__)


Part = namedtuple("Part", ["offset", "length"])


def round_down(a, b):
    return (a // b) * b


def round_up(a, b):
    return ((a + b - 1) // b) * b


class HierarchicalClustering:
    def __init__(self, min_clusters=5):
        self.min_clusters = min_clusters

    def __call__(self, parts):
        clusters = [p for p in parts]

        while len(clusters) > self.min_clusters:
            min_dist = min(
                clusters[i].offset - clusters[i - 1].offset + clusters[i - 1].length
                for i in range(1, len(clusters))
            )
            i = 1
            while i < len(clusters):
                d = clusters[i].offset - clusters[i - 1].offset + clusters[i - 1].length
                if d <= min_dist:
                    clusters[i - 1] = Part(
                        clusters[i - 1].offset,
                        clusters[i].offset
                        + clusters[i].length
                        - clusters[i - 1].offset,
                    )
                    clusters.pop(i)
                else:
                    i += 1

        return clusters

    def __repr__(self):
        return f"cluster({self.min_clusters})"


class BlockGrouping:
    def __init__(self, block_size):
        self.block_size = block_size

    def __call__(self, parts):
        blocks = []
        last_block_offset = -1
        last_offset = 0

        for offset, length in parts:

            assert offset >= last_offset

            block_offset = round_down(offset, self.block_size)
            block_length = round_up(offset + length, self.block_size) - block_offset

            if block_offset <= last_block_offset:
                prev_offset, prev_length = blocks.pop()
                end_offset = block_offset + block_length
                prev_end_offset = prev_offset + prev_length
                block_offset = min(block_offset, prev_offset)
                assert block_offset == prev_offset
                block_length = max(end_offset, prev_end_offset) - block_offset

            blocks.append(Part(block_offset, block_length))

            last_block_offset = block_offset + block_length
            last_offset = offset + length

        return blocks

    def __repr__(self):
        return f"blocked({self.block_size})"


class Automatic:
    def __call__(self, parts):
        smallest = min(x.length for x in parts)
        range_method = round_up(max(x.length for x in parts), 1024)

        while range_method >= smallest:
            blocks = BlockGrouping(range_method)(parts)
            range_method //= 2

        # Max number of parts
        return blocks

    def __repr__(self):
        return "auto"


class Sharp:
    def __init__(self, transfer_rate=1024 * 1024, request_latency_overhead=0.1):
        """
        transfer_rate:
            unit is byte/seconds.
            additional cost to download one useles byte.
         request_latency_overhead:
            unit is seconds.
            additional cost to do one additional HTTP request.
        """
        self.transfer_rate = transfer_rate
        self.request_latency_overhead = request_latency_overhead

    def __call__(self, parts):

        blocks = [parts[0]]

        for offset, length in parts[1:]:
            latest = blocks[-1]
            latest_end = latest.offset + latest.length

            distance = offset - latest_end
            assert distance >= 0, (distance, latest, (offset, length), parts)

            cost_of_merging = (
                distance / self.transfer_rate - self.request_latency_overhead
            )

            if cost_of_merging <= 0:
                blocks[-1] = Part(latest.offset, latest.length + length)
            else:
                blocks.append(Part(offset, length))

        return blocks

    def __repr__(self):
        return f"sharp({self.transfer_rate},{self.request_latency_overhead})"


class Pipe:
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def __call__(self, parts):
        return self.first(self.second(parts))

    def __repr__(self):
        return f"{self.second}|{self.first}"


class Debug:
    def __call__(self, parts):
        print("DEBUG", parts)
        return parts

    def __repr__(self):
        return "debug"


HEURISTICS = {
    "auto": Automatic,
    "sharp": Sharp,
    "cluster": HierarchicalClustering,
    "blocked": BlockGrouping,
    "debug": Debug,
}


def parts_heuristics(method, statistics_gatherer):
    if isinstance(method, int):
        return BlockGrouping(method)

    result = None
    for name in method.split("|"):
        if "(" in name:
            m = re.match(r"(.+)\((.+)\)", name)
            name = m.group(1)
            args = []
            for a in m.group(2).split(","):
                try:
                    args.append(int(a))
                except ValueError:
                    args.append(float(a))
        else:
            args = []

        obj = HEURISTICS[name](*args)
        if result is None:
            result = obj
        else:
            result = Pipe(obj, result)

    statistics_gatherer(
        "parts-heuristics",
        full_method=str(method),
        method_args=args,
    )
    return result
