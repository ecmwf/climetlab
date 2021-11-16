# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
from collections import namedtuple

LOG = logging.getLogger(__name__)


Part = namedtuple("Part", ["offset", "length"])


def round_down(a, b):
    return (a // b) * b


def round_up(a, b):
    return ((a + b - 1) // b) * b


def _positions(parts, blocks):
    # Sanity check
    # Assert that each parts is contain in a rounded part
    i = 0
    positions = []
    roffset, rlength = blocks[i]
    for offset, length in parts:
        while offset > roffset + rlength:
            i += 1
            roffset, rlength = blocks[i]
        start = i
        while offset + length > roffset + rlength:
            i += 1
            roffset, rlength = blocks[i]
        end = i
        assert start == end
        positions.append(offset - blocks[i][0] + sum(blocks[j][1] for j in range(i)))

    return positions


class HierarchicalClustering:
    def __init__(self, min_clusters=5):
        self.min_clusters = min_clusters

    def __call__(self, parts):
        clusters = [Part(offset, length) for offset, length in parts]

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

        return clusters, _positions(parts, clusters)


class BlockGrouping:
    def __init__(self, block_size):
        self.block_size = block_size

    def __call__(self, parts):
        rounded = []
        last_rounded_offset = -1
        last_offset = 0

        for offset, length in parts:

            assert offset >= last_offset

            rounded_offset = round_down(offset, self.block_size)
            rounded_length = round_up(offset + length, self.block_size) - rounded_offset

            if rounded_offset <= last_rounded_offset:
                prev_offset, prev_length = rounded.pop()
                end_offset = rounded_offset + rounded_length
                prev_end_offset = prev_offset + prev_length
                rounded_offset = min(rounded_offset, prev_offset)
                assert rounded_offset == prev_offset
                rounded_length = max(end_offset, prev_end_offset) - rounded_offset

            rounded.append((rounded_offset, rounded_length))

            last_rounded_offset = rounded_offset + rounded_length
            last_offset = offset + length

        return rounded, _positions(parts, rounded)


class Automatic:
    def __call__(self, parts):
        smallest = min(x[1] for x in parts)
        transfer_size = round_up(max(x[1] for x in parts), 1024)

        while transfer_size >= smallest:
            rounded, positions = BlockGrouping(transfer_size)(parts)
            transfer_size //= 2

        return rounded, positions
