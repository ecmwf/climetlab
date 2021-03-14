#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import io
import os.path
import sys

import setuptools


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return io.open(file_path, encoding="utf-8").read()


version = None
for line in read("climetlab/__init__.py").split("\n"):
    if line.startswith("__version__"):
        version = line.split("=")[-1].strip()[1:-1]


assert version

install_requires = []

if sys.platform == "win32":
    if sys.version_info < (3, 9):
        install_requires += ["cftime==1.1.0"]
    else:
        install_requires += ["cftime==1.0.0"]

if sys.version_info < (3, 7):
    install_requires += ["cython", "pandas==1.1.5"]
else:
    install_requires += ["cython", "pandas"]


install_requires += [
    # need to install  to avoid conflict between aiohttp (dependency of s3fs) and requests (cdsapi)
    # "chardet>=3.0,<4.0",
    # "aiohttp>=3.7.2",
    # --
    "requests",
    # "zarr",
    # "s3fs",
    "numpy",
    "xarray>=0.17.0",
    "netcdf4",
    "cfgrib>=0.9.8.4",
    "cdsapi",
    "ecmwf-api-client>=1.6.1",
    "tqdm",
    "requests",
    "eccodes>=0.9.9",
    "magics>=1.5.6",
    "ecmwflibs>=0.0.91",
    "pdbufr",
    "pyodc",
    "dask",
    "toolz",
    "pyyaml",
    "markdown",
    "entrypoints",
]

extra_require = {"interactive": ["skinnywms", "folium"]}


full = []
for k, v in extra_require.items():
    full += v
full += install_requires

extra_require["full"] = full


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
    install_requires=install_requires,
    extra_require=extra_require,
    zip_safe=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
    tests_require=["pytest", "nbconvert", "jupyter", "pytest-cov"],
    test_suite="tests",
)
