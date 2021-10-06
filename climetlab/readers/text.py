# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from . import Reader
from .csv import CSVReader, is_csv


def is_text(path, prob_lines=1000, probe_size=4096):
    try:
        with open(path, "rb") as f:
            if 0x0 in f.read(probe_size):
                return False

        with open(path, "r", encoding="utf-8") as f:
            for i, _ in enumerate(f):
                if i > prob_lines:
                    break
        return True
    except UnicodeDecodeError:
        return False


class TextReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

    def ignore(self):
        # Used by multi-source
        return True

    def mutate(self):
        if is_csv(self.path):
            return CSVReader(self.source, self.path)

        return self


def reader(source, path, magic=None, deeper_check=False):
    if magic is None:  # Bypass check and force
        return TextReader(source, path)

    if deeper_check:
        if is_text(path):
            return TextReader(source, path)
