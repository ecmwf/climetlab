# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab.core import Base
from climetlab.core.index import Index
from climetlab.core.index import MaskIndex
from climetlab.core.index import MultiIndex


class Field(Base):
    pass


class FieldSet(Index):
    @classmethod
    def new_mask_index(self, *args, **kwargs):
        return MaskFieldSet(*args, **kwargs)

    @classmethod
    def merge(cls, sources):
        assert all(isinstance(_, FieldSet) for _ in sources)
        return MultiFieldSet(sources)


class MaskFieldSet(FieldSet, MaskIndex):
    def __init__(self, *args, **kwargs):
        MaskIndex.__init__(self, *args, **kwargs)


class MultiFieldSet(FieldSet, MultiIndex):
    def __init__(self, *args, **kwargs):
        MultiIndex.__init__(self, *args, **kwargs)


class FieldArray(FieldSet):
    def __init__(self, fields=None):
        self.fields = fields if fields is not None else []

    def append(self, field):
        self.fields.append(field)

    def _getitem(self, n):
        return self.fields[n]

    def __len__(self):
        return len(self.fields)

    def __repr__(self) -> str:
        return f"FieldArray({len(self.fields)})"


class UpdateMetadata(Field):
    def __init__(self, field, **kwargs):
        self.field = field
        self.kwargs = kwargs

    def metadata(self, key):

        if key in self.kwargs:
            return self.kwargs[key]

        return self.field.metadata(key)

    def as_mars(self):
        result = self.field.as_mars()
        result.update(self.kwargs)
        return result

    def __getattr__(self, name):
        return getattr(self.field, name)


class UpdateData(Field):
    def __init__(self, field, data):
        self.field = field
        self.data = data

    def to_numpy(self, *args, **kwargs):
        return self.data

    def __getattr__(self, name):
        return getattr(self.field, name)
