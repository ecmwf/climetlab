# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging
import os

import climetlab as cml
from climetlab.readers.grib.index import FieldsetInFilesWithSqlIndex
from climetlab.readers.grib.parsing import GribIndexingDirectoryParserIterator
from climetlab.sources import Source
from climetlab.sources.indexed import IndexedSource
from climetlab.sources.directory import DirectorySource

LOG = logging.getLogger(__name__)


class NoLock:
    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass


class CacheDict(dict):
    def __init__(self, field):
        self.field = field

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            self[key] = self.field[key]
            return self[key]

    def __str__(self):
        return f"{self.field} (cached)"


class VirtualField:
    def __init__(self, getitem, i, owner, reference):

        self._real_item = None

        def get_real_item():
            item = getitem(i)
            print(f"requesting actual field {i:02d}: {item}")
            return item

        self._real_item_func = get_real_item

        self.reference = reference
        self.owner = owner

    @property
    def real_item(self):
        if self._real_item is None:
            self._real_item = self._real_item_func()
        return self._real_item

    def metadata(self, n):
        value = self.real_item[n]
        ref = self.reference[n]

        if str(value) != str(ref):
            print(n, "differs", value, ref)
        # if n == "dataDate":
        #    return self.date

        # if n == "dataTime":
        #    return self.time
        return self.real_item[n]

    @property
    def values(self):
        return self.real_item.to_numpy()

    def to_numpy(self):
        return self.real_item.to_numpy()

    @property
    def shape(self):
        return self.reference.shape

    def __str__(self):
        return "Virt" + str(self.real_item)


class VirtualFieldsetInFilesWithSqlIndex(FieldsetInFilesWithSqlIndex):
    def __init__(self, *args, **kwargs):
        self._reference = None
        super().__init__(*args, **kwargs)

    def xarray_open_dataset_kwargs(self):
        return dict(
            cache=False,  # Set to false to prevent loading the whole dataset
            #        chunks={
            #            "time": 24 * 31,
            #            # "step": 1,
            #            # "number": 1,
            #            # "surface": 1,
            #            "latitude": 721,
            #            "longitude": 1440,
            #        },
            lock=NoLock(),
        )

    def __getitem__(self, n):
        if n >= len(self):
            raise IndexError

        print(f"requesting item {n:02d}")
        item = VirtualField(
            super().__getitem__,
            n,
            owner=self,
            reference=self.reference,
        )
        print(f"                     -> {item}")
        return item

    @property
    def reference(self):
        if self._reference is None:
            reference = super().__getitem__(0)
            self._reference = CacheDict(reference)
            print(f"got reference = {reference}")
        return self._reference


class VirtualDirectorySource(DirectorySource):
    INDEX_CLASS = VirtualFieldsetInFilesWithSqlIndex


source = VirtualDirectorySource
