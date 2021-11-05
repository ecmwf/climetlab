# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

from climetlab.arguments.transformers import (
    AliasTransformer,
    EnumChecker,
    FormatTransformer,
    TypeTransformer,
)

LOG = logging.getLogger(__name__)


def check_included(values1, values2):
    if isinstance(values1, (list, tuple)) and isinstance(values2, (list, tuple)):
        for x in values1:
            if x not in values2:
                raise ValueError(f"'{x}' is not in {values2}")


class Argument:
    def __init__(
        self,
        name,
        decorators,
    ):
        if name is not None:
            assert isinstance(name, str), name
        self.name = name
        self.decorators = decorators
        self._cmltype = None

    @property
    def cmltype(self):
        if self._cmltype:
            return self._cmltype

        type1 = None
        type2 = None

        if self.normalize_decorator:
            return self.normalize_decorator.cml_type

        if self.availability_decorator:
            type2 = self.availability_decorator.gess_cml_type(self.name)

        if type1 and type2:
            assert type1 == type2
        else:
            if type1:
                type = type1
            else:
                type = type2

        if type:
            self._cmltype = type

        return self._cmltype

    @property
    def format(self):
        if not self.normalize_decorator:
            return None
        return self.normalize_decorator.format

    @property
    def aliases(self):
        if self.normalize_decorator:
            return self.normalize_decorator.aliases
        return {}

    @property
    def normalize_decorator(self):
        decos = [d for d in self.decorators if not d.is_availability]
        if decos:
            assert len(decos) == 1, decos
            return decos[0]
        return None

    @property
    def availability_decorator(self):
        decos = [d for d in self.decorators if d.is_availability]
        if decos:
            assert len(decos) == 1, decos
            return decos[0]
        return None

    def add_alias_transformers(self, pipeline):
        if self.aliases:
            pipeline.append(AliasTransformer(self.name, self.cmltype, self.aliases))

    def add_type_transformers(self, pipeline):
        pipeline.append(TypeTransformer(self.name, self.cmltype))

    def add_enum_transformers(self, pipeline):
        values = None
        if self.normalize_decorator and not self.availability_decorator:
            values = self.normalize_decorator.get_values(self.name)

        if not self.normalize_decorator and self.availability_decorator:
            values = self.norm_av.get_values()

        if self.normalize_decorator and self.availability_decorator:
            values1 = self.normalize_decorator.get_values()
            values2 = self.norm_av.get_values()

            def merge_values(value1, value2):
                if values1 and values2:
                    check_included(values1, values2)
                    return values1
                if values1:
                    return value1
                if values2:
                    return value2
                return None

            values = merge_values(values1, values2)

        if values:
            pipeline.append(EnumChecker(self.name, values, type=self.cmltype))

    def add_format_transformers(self, pipeline):
        if self.format is not None:
            pipeline.append(FormatTransformer(self.name, self.cmltype, self.format))
