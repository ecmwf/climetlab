# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging
import warnings
from collections import defaultdict

from climetlab.readers.grib.index import FieldsetInFilesWithSqlIndex
from climetlab.sources.directory import DirectorySource

LOG = logging.getLogger(__name__)

USE_REFERENCE = [
    "distinctLatitudes",
    "distinctLongitudes",
    "gridType",
    "NV",
    "Nx",
    "Ny",
    "paramId",
    "name",
    "shortName",
    "units",
    "dataType",
]
REMOVE = [
    "stepUnits",
    "endStep",
    "numberOfDirections",
    "numberOfFrequencies",
    "directionNumber",
    "frequencyNumber",
    "gridDefinitionDescription",
    "centre",
    "centreDescription",
    "edition",
    "subCentre",
    "stepType",
    "totalNumber",
    "cfName",
    "cfVarName",
    "missingValue",
    "typeOfLevel",
    "jScansPositively",
    "latitudeOfFirstGridPointInDegrees",
    "latitudeOfLastGridPointInDegrees",
    "longitudeOfFirstGridPointInDegrees",
    "longitudeOfLastGridPointInDegrees",
    "numberOfPoints",
    "iDirectionIncrementInDegrees",
    "jDirectionIncrementInDegrees",
    "iScansNegatively",
    "jPointsAreConsecutive",
]


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
    # DEBUG = True
    DEBUG = False
    _real_item = None

    def __init__(self, i, owner, reference):
        self.i = i
        self.owner = owner
        self.item_metadata = owner.get_metadata(i)
        self.reference, self.ref_metadata = reference

    @property
    def real_item(self):
        return self.owner.get_real_item(self.i)

    def _from_real_item(self, key):
        assert self.DEBUG is True
        return self.real_item[key]

    def _check_with_real_item(self, key, value, desc):
        real = self._from_real_item(key)
        if type(real) != type(value) or str(real) != str(value):
            warnings.warn(
                f"{key}: From {desc}: providing {value} (type {type(value)}) instead of {real} (type {type(real)})"
            )
            print(
                f"{key}: From {desc}: providing {value} (type {type(value)}) instead of {real} (type {type(real)})"
            )
            exit(-1)
        return True

    def metadata(self, key):
        if key in REMOVE:
            return None

        def ref(k):
            value = self.reference[k]
            if self.DEBUG:
                self._check_with_real_item(k, value, "reference")
            return value

        def from_reference_with_warning(k):
            value = ref(k)
            warnings.warn(f"Reading from reference (not expected): {k}={value}")
            return value

        find_metadata = defaultdict(lambda: from_reference_with_warning)

        def check(k):
            r = self.ref_metadata[k]
            i = self.item_metadata[k]
            if r != i:
                raise Exception(f"Error for key={k}: ref={r}, item={i}")

        check("md5_grid_section")
        for k in USE_REFERENCE:
            find_metadata[k] = ref

        check("param")
        find_metadata["param"] = lambda x: self.item_metadata["param"]
        find_metadata["shortName"] = lambda x: self.item_metadata["param"]
        find_metadata["number"] = lambda x: int(self.item_metadata["number"])
        find_metadata["level:float"] = lambda x: float(self.item_metadata["levelist"])
        find_metadata["level"] = lambda x: int(self.item_metadata["levelist"])
        find_metadata["dataDate"] = lambda x: int(self.item_metadata["date"])
        find_metadata["dataTime"] = lambda x: int(self.item_metadata["time"])

        func = find_metadata[key]
        try:
            value = func(key)
        except Exception as e:
            warnings.warn(f"Exception reading {key}:{str(e)}")
            if self.DEBUG:
                print(f"Exception reading {key}: {str(e)}")
                exit(-1)

        if self.DEBUG:
            self._check_with_real_item(key, value, "final-check")

        return value

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
            cache=False,  # Set to False to prevent loading the whole dataset
            # chunks={ },
            lock=NoLock(),
        )

    def get_real_item(self, n):
        return super().__getitem__(n)

    def __getitem__(self, n):
        if n >= len(self):
            raise IndexError

        item = VirtualField(n, owner=self, reference=self.reference)
        return item

    @property
    def reference(self):
        if self._reference is None:
            reference = self.get_real_item(0)
            metadata = self.get_metadata(0)
            self._reference = (CacheDict(reference), metadata)
        return self._reference


class VirtualDirectorySource(DirectorySource):
    INDEX_CLASS = VirtualFieldsetInFilesWithSqlIndex


source = VirtualDirectorySource
