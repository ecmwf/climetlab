# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import weakref

ANNOTATIONS = []


def free_slot():
    for i, a in enumerate(ANNOTATIONS):
        if a is None:
            return i
        if a.owner is None:
            return i
    ANNOTATIONS.append(None)
    return len(ANNOTATIONS) - 1


class Annotation:
    def __init__(self, owner, **kwargs):
        self._owner = None if owner is None else weakref.ref(owner)
        self._kwargs = kwargs

    def get(self, name):
        return self._kwargs.get(name)

    @property
    def owner(self):
        if self._owner is None:
            return None
        return self._owner()

    def __repr__(self):
        return repr(self._kwargs)


def _annotate_pandas(pd, owner, **kargs):

    n = None
    for i, a in enumerate(pd._metadata):
        if isinstance(a, str) and a.startswith("climetlab-"):
            n = i

    if n is None:
        n = len(pd._metadata)
        pd._metadata.append(None)

    slot = free_slot()
    pd._metadata[n] = "climetlab-{}".format(slot)

    ANNOTATIONS[slot] = Annotation(owner, **kargs)


def _annotation_pandas(pd):
    for a in pd._metadata:
        if isinstance(a, str) and a.startswith("climetlab-"):
            _, i = a.split("-")
            return ANNOTATIONS[int(i)]

    return Annotation(None)


def _annotate_xarray(xr, owner, **kargs):
    xr.climetlab._metadata = Annotation(owner, **kargs)


def _annotation_xarray(xr):
    return xr.climetlab._metadata


def annotate(obj, owner, **kwargs):
    if hasattr(obj, "_metadata"):
        _annotate_pandas(obj, owner, **kwargs)
        return obj

    if hasattr(obj, "climetlab"):
        _annotate_xarray(obj, owner, **kwargs)
        return obj

    raise NotImplementedError("Cannot annotate object of type", type(obj))


def annotation(obj):
    if hasattr(obj, "_metadata"):
        return _annotation_pandas(obj)

    if hasattr(obj, "climetlab"):
        return _annotation_xarray(obj)

    raise NotImplementedError("Cannot annotate object of type", type(obj))


class XMetadata:
    def __init__(self, xarray_obj):
        # self._obj = xarray_obj
        self._metadata = Annotation(None)


class XDataset(XMetadata):
    def __init__(self, xarray_obj):
        super().__init__(xarray_obj)


class XDataArray(XMetadata):
    def __init__(self, xarray_obj):
        super().__init__(xarray_obj)


try:
    import xarray as xr

    xr.register_dataset_accessor("climetlab")(XDataset)
    xr.register_dataarray_accessor("climetlab")(XDataArray)
except Exception:
    pass


def init_metadata():
    # Dummy function so climetlab.__init__ loads that file
    # and the xarray accessors are registered
    pass
