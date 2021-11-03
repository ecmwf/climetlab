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
    FormatTransformer,
    MultipleTransformer,
    NormalizeTransformer,
    TypeTransformer,
)

LOG = logging.getLogger(__name__)


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

    def add_alias_transformers(self, pipeline):
        aliases = dict()
        for decorator in self.decorators:
            a = decorator.get_aliases()
            # assert a not incompatible with aliases
            if a is not None:
                aliases.update(a)

        if aliases:
            pipeline.append(AliasTransformer(self.name, aliases))

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
            type = self.norm_deco.get_type()

        if not self.norm_deco and self.av_deco:
            type = self.av_deco.get_type(self.name)

        if self.norm_deco and self.av_deco:
            type1 = self.av_deco.get_type()
            type2 = self.av_deco.get_type(self.name)
            if type1 and type2:
                assert type1 == type2, (type1, type2)
            if type1:
                type = type1
            if type2:
                type = type2

        if type:
            pipeline.append(TypeTransformer(self.name, type))

    def add_canonicalize_transformers(self, pipeline):

        norm = [d for d in self.decorators if not d.is_availability]
        avail = [d for d in self.decorators if d.is_availability]

        assert len(norm) <= 1
        assert len(avail) <= 1

        if avail and not norm:
            pipeline.append(
                NormalizeTransformer(
                    self.name,
                    avail[0].get_values(self.name),
                )
            )
            return

        if norm and not avail:
            pipeline.append(
                NormalizeTransformer(
                    self.name,
                    norm[0].norm,
                )
            )
            return

        if norm and avail:
            nv = norm[0].get_values(self.name)
            av = avail[0].get_values(self.name)
            if av and nv:
                for x in nv:
                    if x not in av:
                        raise ValueError(f"'{x}' is not in {av}")
            vals = nv if nv is not None else av
            if nv is None:
                pipeline.append(
                    NormalizeTransformer(
                        self.name,
                        vals,
                    )
                )
            return

        assert False

    def add_format_transformers(self, pipeline):
        format = None
        for decorator in self.decorators:
            a = decorator.get_format()
            # assert a not incompatible with formats
            if a is not None:
                format = a

        if format is not None:
            pipeline.append(FormatTransformer(self.name, format))

    def add_multiple_transformers(self, pipeline):
        multiple = None
        for decorator in self.decorators:
            a = decorator.get_multiple()
            # assert a not incompatible with multiples
            if a is not None:
                multiple = a

        if multiple is not None:
            pipeline.append(MultipleTransformer(self.name, multiple))
