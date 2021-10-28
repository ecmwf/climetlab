# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import logging

LOG = logging.getLogger(__name__)

KEYWORDS = ["alias", "normalize", "availability", "multiple", "format", "type"]


class Argument:
    def __init__(
        self, name, values=None, alias=None, multiple=None, format=None, type=None
    ):
        self.name = name
        if alias is None:
            alias = {}

        self._data = {k: None for k in KEYWORDS}
        self._decorators = []

        if isinstance(values, tuple):
            self._data["multiple"] = False
        elif isinstance(values, list):
            self._data["multiple"] = True

        self._data["alias"] = alias
        self._data["values"] = values
        self._data["multiple"] = multiple
        self._data["format"] = format
        self._data["type"] = type

        # self.validate()

    def add_deco(self, deco):
        print("Adding decorator ", deco)
        if deco.name != self.name:
            return
        self._decorators.append(deco)

    def merge_decorators(self):
        self._data["alias"] = self.merged_alias("alias")
        self._data["multiple"] = self.merged_multiple("multiple")
        self._data["format"] = self.merged_format("format")
        self._data["type"] = self.merged_type("type")
        self._data["values"] = self.merged_values("values")

    def merged_values(self, key):
        return self.merged_generic(key)

    def merged_format(self, key):
        return self.merged_generic(key)

    def merged_type(self, key):
        return self.merged_generic(key)

    def merged_generic(self, key):
        many = self._decorators
        out = None
        if not many:
            return out
        for deco in many:
            x = deco.get(key)
            if x is None:
                continue
            if out is None:
                out = x
                continue
            if x != out:
                raise Exception(f"Inconsistent values for {key}: {x} != {out}")
        return out

    def merged_alias(self, key):
        many = self._decorators
        out = {}
        if not many:
            return out
        for deco in many:
            v = deco.get(key)
            if v is None or v == {}:
                continue
            if isinstance(v, dict) and isinstance(out, dict):
                LOG.debug(f"Multiple alias values. Merging {out} and {v}.")
                out.update(v)
                continue
            if out is None or out == {}:
                out = v
                continue
            raise ValueError(f"Multiple alias values. Cannot merge {out} and {v}.")
        return out

    def merged_multiple(self, key):
        many = self._decorators
        out = None
        if not many:
            return out
        for deco in many:
            x = deco.get("multiple")
            if x is None:
                continue
            if out is None:
                out = x
                continue
            if x != out:
                raise Exception(f"Inconsistent values for {key}")
        if not out is None:
            return out

        for deco in many:
            values = deco.get("values")
            if isinstance(values, tuple):
                x = False
            if isinstance(values, list):
                x = True
            if x is None:
                continue
            if out is None:
                out = x
                continue
            if x != out:
                raise Exception(f"Inconsistent implicit values for {key}")
        if not out is None:
            return out
        return None

    def __repr__(self) -> str:
        txt = "-- " + str(self.name) + "\n"
        for k, v in self._data.items():
            if v is None:
                continue
            txt += f"    {k}={v}\n"
        txt += "  decorators:\n"
        for d in self._decorators:
            txt += f"    {d}\n"
        return txt

    def validate(self):
        pass
        # if self.count_decorators("multiple") > 1:
        #    LOG.warn(f"Multiple value for 'multiple' provided for {self.name}")

        # if self.count_decorators("alias") > 1:
        #    LOG.warn(f"Multiple value for 'alias' provided for {self.name}")

    def __call__(self, value):
        from .input_manager import InputManager
        arguments = InputManager([self])
        return arguments.apply_to_kwargs({self.name: value})[self.name]