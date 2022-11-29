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
from climetlab.utils import progress_bar

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
METADATA_FUNCS = defaultdict(lambda x, item: item.owner.from_reference(x, item))

for k in REMOVE:
    METADATA_FUNCS[k] = lambda x, item: None

for k in USE_REFERENCE:
    METADATA_FUNCS[k] = lambda x, item: item.owner.from_reference(x, item)


def cast_or_none(typ, key):
    def f(x, item):
        value = item.item_metadata[key]
        if value is None:
            return None
        value = typ(value)
        return value

    return f


METADATA_FUNCS["param"] = lambda x, item: item.item_metadata["param"]
METADATA_FUNCS["shortName"] = lambda x, item: item.item_metadata["param"]
METADATA_FUNCS["number"] = cast_or_none(int, "number")
METADATA_FUNCS["level:float"] = cast_or_none(float, "levelist")
METADATA_FUNCS["level"] = cast_or_none(int, "levelist")
METADATA_FUNCS["dataDate"] = lambda x, item: int(item.item_metadata["date"])
METADATA_FUNCS["dataTime"] = lambda x, item: int(item.item_metadata["time"])


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


class VirtualField:  # Should inherit from GribField

    _real_item = None

    def __init__(self, i, owner):
        self.i = i
        self.owner = owner
        self.item_metadata = owner.get_metadata(i)

    @property
    def DEBUG(self):
        return self.owner.DEBUG

    @property
    def real_item(self):
        if self._real_item is None:
            self._real_item = self.owner.get_real_item(self.i)
        return self._real_item

    def write(self, f):
        return self.real_item.write(f)

    def metadata(self, key):
        return self.owner._get_metadata_for_item(key, self)

    @property
    def values(self):
        return self.real_item.to_numpy()

    def to_numpy(self):
        return self.real_item.to_numpy()

    @property
    def shape(self):
        return self.owner.reference[0].shape

    def __str__(self):
        return "Virt" + str(self.real_item)


class VirtualFieldsetInFilesWithSqlIndex(FieldsetInFilesWithSqlIndex):
    # DEBUG = True
    DEBUG = False

    def __init__(self, *args, **kwargs):
        self._reference = None
        self.pbar = None
        super().__init__(*args, **kwargs)

    def xarray_open_dataset_kwargs(self):
        return dict(
            cache=False,  # Set to False to prevent loading the whole dataset
            # chunks={ },
            lock=NoLock(),
        )

    def __getitem__(self, n):
        if n >= len(self):
            raise IndexError
        if self.pbar:
            self.pbar.update(1)

        item = VirtualField(n, owner=self)

        self.check_same_metadata_as_reference("md5_grid_section", item)
        self.check_same_metadata_as_reference("param", item)

        return item

    def get_real_item(self, n):
        return super().__getitem__(n)

    def _get_metadata_for_item(self, key, item):

        func = METADATA_FUNCS[key]

        try:
            value = func(key, item)
        except Exception as e:
            LOG.exception(f"Exception reading {key}:{str(e)}")
            return None

        if key not in METADATA_FUNCS:
            warnings.warn(f"Reading from reference (not expected): {k}={func(k)}")

        if item.DEBUG:
            if key not in REMOVE:
                self._check_with_real_item(key, item, value)
            else:
                assert value is None, (key, value)

        return value

    def to_xarray(self, *args, **kwargs):
        self.pbar = progress_bar(desc="to xarray()", total=len(self))
        ds = super().to_xarray(*args, **kwargs)
        self.pbar = None
        return ds

    @property
    def reference(self):
        if self._reference is None:
            reference = self.get_real_item(0)
            metadata = self.get_metadata(0)
            self._reference = (CacheDict(reference), metadata)
        return self._reference

    def from_reference(self, key, item):
        value = self.reference[0][key]
        return value

    def _check_with_real_item(self, key, item, value):
        assert self.DEBUG is True
        real = item.real_item[key]
        if type(real) != type(value) or str(real) != str(value):
            msg = f"key={key}: providing {value} (type {type(value)}) instead of {real} (type {type(real)})"
            warnings.warn(msg)
            exit(-1)
        return True

    def check_same_metadata_as_reference(self, key, item):
        r = self.reference[1][key]
        i = item.item_metadata[key]
        if r != i:
            raise Exception(
                (
                    f"Error for field={item.i} and {key=}:"
                    " the reference field metadata is {r=}"
                    " but the metatada for the item is {i=}"
                )
            )


class VirtualDirectorySource(DirectorySource):
    INDEX_CLASS = VirtualFieldsetInFilesWithSqlIndex


source = VirtualDirectorySource
