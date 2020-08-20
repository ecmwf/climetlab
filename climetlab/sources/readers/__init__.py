# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import os
import weakref


class Reader:
    def __init__(self, source, path):
        self._source = weakref.ref(source)
        self.path = path

    @property
    def source(self):
        return self._source()


def grib_reader(source, path):
    from .grib import GRIBReader

    return GRIBReader(source, path)


def bufr_reader(source, path):
    from .bufr import BUFRReader

    return BUFRReader(source, path)


def netcdf_reader(source, path):
    from .netcdf import NetCDFReader

    return NetCDFReader(source, path)


def odb_reader(source, path):
    from .odb import ODBReader

    return ODBReader(source, path)


def csv_reader(source, path):
    from .csv import CSVReader

    return CSVReader(source, path)


def zip_reader(source, path):
    from .zip import ZIPReader

    return ZIPReader(source, path)


READERS = {
    b"GRIB": grib_reader,
    b"BUFR": bufr_reader,
    b"\x89HDF": netcdf_reader,
    b"CDF\x01": netcdf_reader,
    b"CDF\x02": netcdf_reader,
    b"\xff\xffOD": odb_reader,
    b"PK\x03\x04": zip_reader,
    ".csv": csv_reader,
}


def reader(source, path):

    _, extension = os.path.splitext(path)
    if extension in READERS:
        return READERS[extension](source, path)

    with open(path, "rb") as f:
        header = f.read(4)

    if header in READERS:
        return READERS[header](source, path)

    raise ValueError(
        "Unsupported file {} (header={}, extension={})".format(path, header, extension)
    )
