# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.sources import Source


class TestingMockup:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class TestingXarrayAttrs(dict):
    pass


class TestingXarrayDims(list):
    pass


class TestingDatasetAsXarray(TestingMockup):
    def __init__(self, *args, **kwargs):
        super(TestingDatasetAsXarray, self).__init__(*args, **kwargs)
        self.attrs = TestingXarrayAttrs()
        self.dims = TestingXarrayDims()

    # TODO: make this generic
    def min(self, *args, **kwargs):
        print(f"xr.min({args}, {kwargs})")
        return 42.0

    def max(self, *args, **kwargs):
        print(f"xr.min({args}, {kwargs})")
        return 42.0

    def map(self, *args, **kwargs):
        print("xr.map(...)")
        # print(f'xr.map({args}, {kwargs})')
        return self

    def sortby(self, *args, **kwargs):
        print(f"xr.sortby({args}, {kwargs})")
        return self

    def __getitem__(self, key):
        print(f"xr.__getitem__({key})")
        return self

    def __setitem__(self, key, value):
        print(f"xr.__setitem__({key})=...")
        # print(f'xr.__setitem__({key})={value}')
        return self

    def chunk(self, *args, **kwargs):
        print(f"xr.chunk({args}, {kwargs})")
        return self

    def astype(self, *args, **kwargs):
        print(f"xr.astype({args}, {kwargs})")
        return self

    def to_zarr(self, *args, **kwargs):
        print(f"xr.to_zarr({args}, {kwargs})")
        return self

    def __getattr__(self, name):
        print(f"xr.{name} (unkwown)")
        return self


class DatasetMockup(TestingMockup):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        print(f"Climetlab SourceMockup : args={args}, kwargs={kwargs}")
        super(SourceMockup, self).__init__(**kwargs)

    def to_xarray(self, *args, **kwargs):
        return TestingDatasetAsXarray(*self.args, **self.kwargs)


class SourceMockup(Source):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        print(f"Climetlab SourceMockup : args={args}, kwargs={kwargs}")
        super(SourceMockup, self).__init__(**kwargs)

    def to_xarray(self, *args, **kwargs):
        return TestingDatasetAsXarray(*self.args, **self.kwargs)
