#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#


import io
import os.path

import setuptools


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return io.open(file_path, encoding="utf-8").read()


version = None
for line in read("climetlab/__init__.py").split("\n"):
    if line.startswith("__version__"):
        version = line.split("=")[-1].strip()[1:-1]


assert version

setuptools.setup(
    name="climetlab",
    version=version,
    author="ECMWF",
    author_email="software.support@ecmwf.int",
    license="Apache 2.0",
    url="https://github.com/ecmwf/climetlab",
    description="Handling of climate/meteorological data",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas==1.0.5",  # Magics xarray does not work with pandas 1.1.0
        "numpy",
        "xarray",
        "netcdf4",
        "cfgrib>=0.9.8.4",
        "cdsapi",
        "ecmwf-api-client",
        "tqdm",
        "requests",
        "eccodes>=0.9.9",
        "magics>=1.3.0",
        "ecmwflibs",
        "pdbufr",
        "pyodc",
        "dask",
        "toolz",
    ],
    zip_safe=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
)
