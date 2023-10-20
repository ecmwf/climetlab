# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import math
import os
from abc import abstractmethod

from climetlab.core.index import Index, MaskIndex, MultiIndex
from climetlab.decorators import normalize_grib_key_values, normalize_grib_keys
from climetlab.indexing.database import (
    FILEPARTS_KEY_NAMES,
    MORE_KEY_NAMES,
    MORE_KEY_NAMES_WITH_UNDERSCORE,
    STATISTICS_KEY_NAMES,
)
from climetlab.readers.grib.codes import GribField
from climetlab.readers.grib.fieldset import FieldSetMixin
from climetlab.utils import progress_bar
from climetlab.utils.availability import Availability

LOG = logging.getLogger(__name__)


class FieldSet(FieldSetMixin, Index):
    _availability = None

    def __init__(self, *args, **kwargs):
        if self.availability_path is not None and os.path.exists(
            self.availability_path
        ):
            self._availability = Availability(self.availability_path)

        Index.__init__(self, *args, **kwargs)

    @classmethod
    def new_mask_index(self, *args, **kwargs):
        return MaskFieldSet(*args, **kwargs)

    @property
    def availability_path(self):
        return None

    @classmethod
    def merge(cls, sources):
        assert all(isinstance(_, FieldSet) for _ in sources)
        return MultiFieldSet(sources)

    def available(self, request, as_list_of_dicts=False):
        from climetlab.utils.availability import Availability

        if not request:
            return None, None

        @normalize_grib_keys
        def f(**_):
            return _

        request = f(**request)
        request = normalize_grib_key_values(request, as_tuple=True)

        keys = list(request.keys())

        ds = self.sel(**request)

        def dicts():
            for i in progress_bar(
                iterable=range(len(ds)),
                desc="Building availability",
            ):
                metadata = ds.get_metadata(i)
                dic = {k: metadata.get(k, "-") for k in keys}
                dic = normalize_grib_key_values(dic, as_tuple=False)
                yield dic

        available = Availability(dicts())

        missing = available.missing(**request)

        if as_list_of_dicts:
            # available = available.as_list_of_dicts()
            # missing = missing.as_list_of_dicts()
            raise NotImplementedError()

        return dict(available=available, missing=missing)

    def _custom_availability(
        self, keys=None, ignore_keys=None, filter_keys=lambda k: True
    ):
        def dicts():
            for i in progress_bar(
                iterable=range(len(self)), desc="Building availability"
            ):
                if keys is not None:
                    dic = self.get_metadata(i)
                    dic = {k: str(dic.get(k, "-")) for k in keys}
                else:
                    dic = self.get_metadata(i)

                    for k in list(dic.keys()):
                        if not filter_keys(k):
                            dic.pop(k)
                            continue
                        if ignore_keys and k in ignore_keys:
                            dic.pop(k)
                            continue
                        if dic[k] is None:
                            dic.pop(k)
                            continue

                yield dic

        from climetlab.utils.availability import Availability

        return Availability(dicts())

    @property
    def availability(self):
        if self._availability is not None:
            return self._availability
        LOG.debug("Building availability")

        self._availability = self._custom_availability(
            ignore_keys=FILEPARTS_KEY_NAMES
            + STATISTICS_KEY_NAMES
            + MORE_KEY_NAMES_WITH_UNDERSCORE
            + MORE_KEY_NAMES
        )
        return self.availability

    def is_full_hypercube(self):
        non_empty_coords = {
            k: v
            for k, v in self.availability._tree.unique_values().items()
            if len(v) > 1
        }
        expected_size = math.prod([len(v) for k, v in non_empty_coords.items()])
        return len(self) == expected_size

    @normalize_grib_keys
    def _normalize_kwargs_names(self, **kwargs):
        return kwargs


class MaskFieldSet(FieldSet, MaskIndex):
    def __init__(self, *args, **kwargs):
        MaskIndex.__init__(self, *args, **kwargs)


class MultiFieldSet(FieldSet, MultiIndex):
    def __init__(self, *args, **kwargs):
        MultiIndex.__init__(self, *args, **kwargs)


class FieldSetInFiles(FieldSet):
    # Remote Fieldsets (with urls) are also here,
    # as the actual fieldset is accessed on a file in cache.
    # This class changes the interface (_getitem__ and __len__)
    # into the interface (part and number_of_parts).
    def _getitem(self, n):
        part = self.part(n)
        return GribField(part.path, part.offset, part.length)

    def __len__(self):
        return self.number_of_parts()

    @abstractmethod
    def part(self, n):
        self._not_implemented()

    @abstractmethod
    def number_of_parts(self):
        self._not_implemented()
