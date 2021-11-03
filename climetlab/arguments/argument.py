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
    CanonicalTransformer,
    FormatTransformer,
    MultipleTransformer,
    TypeTransformer,
)

LOG = logging.getLogger(__name__)


def check_consistency(values1, values2):
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

        if self.norm_deco:
            self._cmltype = self.norm_deco.get_cml_type()

        if self.av_deco:
            self._cmltype = self.av_deco.get_cml_type(self.name)

        return self._cmltype

    def add_alias_transformers(self, pipeline):
        aliases = dict()
        _all = None
        for decorator in self.decorators:
            a = decorator.get_aliases()
            if a is None:
                continue
            if not aliases:
                aliases = a
                multiple = decorator.get_multiple()
                if multiple:
                    _all = decorator.get_values(self.name)
                continue
            if isinstance(aliases, dict) and isinstance(a, dict):
                aliases.update(a)
                continue
            raise ValueError(f"Cannot merge aliases {a} and {aliases}.")

        if aliases:
            pipeline.append(AliasTransformer(self.name, aliases, _all))

    @property
    def norm_deco(self):
        decos = [d for d in self.decorators if not d.is_availability]
        if decos:
            assert len(decos) == 1, decos
            return decos[0]
        return None

    @property
    def av_deco(self):
        decos = [d for d in self.decorators if d.is_availability]
        if decos:
            assert len(decos) == 1, decos
            return decos[0]
        return None

    def add_type_transformers(self, pipeline):
        type = None
        if self.norm_deco and not self.av_deco:
            type = self.norm_deco.get_cml_type()

        if not self.norm_deco and self.av_deco:
            type = self.av_deco.get_cml_type(self.name)

        if self.norm_deco and self.av_deco:
            type1 = self.av_deco.get_cml_type()
            type2 = self.av_deco.get_cml_type(self.name)
            if type1 and type2:
                assert type1 == type2, (type1, type2)
            if type1:
                type = type1
            if type2:
                type = type2

        if type:
            pipeline.append(TypeTransformer(self.name, type))

    def add_canonicalize_transformers(self, pipeline):
        if self.norm_deco and not self.av_deco:
            values = self.norm_deco.get_values(self.name)
            pipeline.append(CanonicalTransformer(self.name, values))

        if not self.norm_deco and self.av_deco:
            values = self.norm_av.get_values()
            pipeline.append(CanonicalTransformer(self.name, values))

        if self.norm_deco and self.av_deco:
            values1 = self.norm_deco.get_values()
            values2 = self.norm_av.get_values()
            if values1 and values2:
                check_consistency(values1, values2)
                pipeline.append(CanonicalTransformer(self.name, values1))
                return
            if values1:
                pipeline.append(CanonicalTransformer(self.name, values1))
                return
            if values2:
                pipeline.append(CanonicalTransformer(self.name, values2))
                return

    def add_format_transformers(self, pipeline):
        type = None
        for decorator in self.decorators:
            t = decorator.get_cml_type()
            if t is not None:
                type = t

        if type is not None:
            pipeline.append(
                FormatTransformer(
                    self.name,
                    type=type,
                )
            )

    def add_multiple_transformers(self, pipeline):
        multiple = None
        for decorator in self.decorators:
            a = decorator.get_multiple()
            # assert a not incompatible with multiples
            if a is not None:
                multiple = a

        if multiple is not None:
            pipeline.append(MultipleTransformer(self.name, multiple))
