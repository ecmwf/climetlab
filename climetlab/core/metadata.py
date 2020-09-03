# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json


# import xarray as xr


# @xr.register_dataset_accessor("climetlab")
# class CliMetLabAccessor:
#     def __init__(self, xarray_obj):
#         self._obj = xarray_obj
#         print("CliMetLabAccessor")
#     def foo(self, v):
#         print("foo", v)


class Annotation:
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def get(self, name):
        return self._kwargs.get(name)


def annotate(pd, **kargs):

    kargs["climetlab"] = "annotation"

    for i, a in enumerate(pd._metadata):
        try:
            a = json.loads(a)
            if a["climetlab"] == "annotation":
                pd._metadata[i] = json.dumps(kargs)
                return pd
        except Exception:
            pass

    pd._metadata.append(json.dumps(kargs))
    return pd


def annotation(pd):
    for a in pd._metadata:
        try:
            a = json.loads(a)
            if a["climetlab"] == "annotation":
                return Annotation(**a)
        except Exception:
            pass
    return Annotation()
