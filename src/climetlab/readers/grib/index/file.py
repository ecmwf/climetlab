# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import json
import logging
import os

from climetlab.core.caching import auxiliary_cache_file
from climetlab.readers.grib.codes import get_messages_positions
from climetlab.readers.grib.index import FieldSetInFiles
from climetlab.utils.parts import Part

LOG = logging.getLogger(__name__)


class FieldSetInOneFile(FieldSetInFiles):
    VERSION = 1

    @property
    def availability_path(self):
        return os.path.join(self.path, ".availability.pickle")

    def __init__(self, path, **kwargs):
        assert isinstance(path, str), path

        self.path = path
        self.offsets = None
        self.lengths = None
        self.mappings_cache_file = auxiliary_cache_file(
            "grib-index",
            path,
            content="null",
            extension=".json",
        )

        if not self._load_cache():
            self._build_offsets_lengths_mapping()

        super().__init__(**kwargs)

    def _build_offsets_lengths_mapping(self):
        offsets = []
        lengths = []

        for offset, length in get_messages_positions(self.path):
            offsets.append(offset)
            lengths.append(length)

        self.offsets = offsets
        self.lengths = lengths

        self._save_cache()

    def _save_cache(self):
        try:
            with open(self.mappings_cache_file, "w") as f:
                json.dump(
                    dict(
                        version=self.VERSION,
                        offsets=self.offsets,
                        lengths=self.lengths,
                    ),
                    f,
                )
        except Exception:
            LOG.exception("Write to cache failed %s", self.mappings_cache_file)

    def _load_cache(self):
        try:
            with open(self.mappings_cache_file) as f:
                c = json.load(f)
                if not isinstance(c, dict):
                    return False

                assert c["version"] == self.VERSION
                self.offsets = c["offsets"]
                self.lengths = c["lengths"]
                return True
        except Exception:
            LOG.exception("Load from cache failed %s", self.mappings_cache_file)

        return False

    def part(self, n):
        return Part(self.path, self.offsets[n], self.lengths[n])

    def number_of_parts(self):
        return len(self.offsets)
