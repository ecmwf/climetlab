# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

from climetlab.arguments.climetlab_types import infer_type
from climetlab.arguments.transformers import (
    AliasTransformer,
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
    ):
        assert name != "format"
        self.name = name
        self.normalize = {}
        self.availability = None
        self._type = None

    @property
    def cmltype(self):
        if self._type is None:
            self.format = self.normalize.get("format")
            self.normalize.setdefault("values", self.availability)
            self._type = infer_type(**self.normalize)
        return self._type

    @property
    def aliases(self):
        return self.normalize.get("aliases", {})

    def add_alias_transformers(self, pipeline):
        if self.aliases:
            pipeline.append(AliasTransformer(self, self.cmltype, self.aliases))

    def add_type_transformers(self, pipeline):
        pipeline.append(TypeTransformer(self, self.cmltype))

    def add_format_transformers(self, pipeline):
        if self.format is not None:
            pipeline.append(FormatTransformer(self, self.format, self.cmltype))

    def set_default(self, default):
        raise NotImplementedError("default TODO")

    def __repr__(self) -> str:
        return f"Argument({self.name})"
