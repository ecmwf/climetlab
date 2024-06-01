# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import mimetypes

from .metadata import init_metadata

mimetypes.add_type("application/x-netcdf", ".nc")
mimetypes.add_type("application/x-netcdf", ".nc4")
mimetypes.add_type("application/x-netcdf", ".cdf")
mimetypes.add_type("application/x-netcdf", ".netcdf")

mimetypes.add_type("application/x-grib", ".grib")
mimetypes.add_type("application/x-grib", ".grib1")
mimetypes.add_type("application/x-grib", ".grib2")


def initialise():
    init_metadata()
