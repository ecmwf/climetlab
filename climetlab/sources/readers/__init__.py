# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

def grib_reader(path):
    from .grib import GRIBReader
    return GRIBReader(path)


def bufr_reader(path):
    from .bufr import BUFRReader
    return BUFRReader(path)


def netcdf_reader(path):
    from .netcdf import NetCDFReader
    return NetCDFReader(path)


def odb_reader(path):
    from .odb import ODBReader
    return ODBReader(path)


READERS = {
    b'GRIB': grib_reader,
    b'BUFR': bufr_reader,
    b'\x89HDF': netcdf_reader,
    b'CDF\x01': netcdf_reader,
    b'CDF\x02': netcdf_reader,
    b'\xff\xffOD': odb_reader,
}


def reader(path):
    with open(path, 'rb') as f:
        header = f.read(4)

    if header in READERS:
        return READERS[header](path)

    raise ValueError('Unsupported file {} (header={})'.format(path, header))
