# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


class Flavour:
    def __init__(self, name, reader):
        self.name = name
        self.reader = reader
        self._cache = {}

    def __repr__(self):
        return f"<Flavour {self.name}>"

    def metadata(self, field, key):
        return getattr(self, f"get_{key}")(field)

    def get_valid_datetime(self, field):
        return field.time.isoformat()

    def get_param(self, field):
        return field.variable

    def get_levelist(self, field):
        return field.levelist

    def get_levtype(self, field):
        return field.levtype

    def get_number(self, field):
        return None

    def get_area(self, field):
        return None

    def get_grid(self, field):
        return None

    def get_resolution(self, field):
        return None

    def get_step(self, field):
        return field.step

    def as_mars(self, field):
        return dict(
            param=self.get_param(field),
            levelist=self.get_levelist(field),
            number=self.get_number(field),
            levtype=self.get_levtype(field),
        )


def get_flavour(reader, flavour):
    return Flavour("default", reader)
