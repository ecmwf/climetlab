# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


class GribOutput:
    def __init__(self, filename, template=None, **kwargs):
        self.f = open(filename, "wb")
        self.template = template

    def write(self, values, metadata={}, template=None):
        if template is None:
            template = self.template

        handle = template.handle.clone()
        handle.set_values(values)
        for k, v in metadata.items():
            handle.set(k, v)
        handle.write(self.f)

    def close(self):
        self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trace):
        self.close()


def new_grib_output(*args, **kwargs):
    return GribOutput(*args, **kwargs)
