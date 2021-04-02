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

numpy = "numpy"
pandas = "pandas"
dask = "dask"

install_requires = []
if sys.version_info < (3, 7):
    install_requires += [
        "numpy<1.20",
        "pandas==1.1.5",
        "dataclasses",  # Needed by dask
    ]
else:
    install_requires += ["numpy", "pandas"]

install_requires += [
    # need to install  to avoid conflict between aiohttp (dependency of s3fs) and requests (cdsapi)
    # "chardet>=3.0,<4.0",
    # "aiohttp>=3.7.2",
    # --
    "requests",
    # "zarr",
    # "s3fs",
    "xarray>=0.17.0",
    "dask",
    "netcdf4",
    "cfgrib>=0.9.8.4",
    "cdsapi",
    "ecmwf-api-client>=1.6.1",
    "tqdm",
    "eccodes>=0.9.9",
    "magics>=1.5.6",
    "ecmwflibs>=0.1.2",
    "pdbufr",
    "pyodc",
    "toolz",
    "pyyaml",
    "markdown",
    "entrypoints",
    "branca==0.3.1",  # See https://github.com/python-visualization/branca/issues/81"
    "folium>=0.12.1",
]

extras_require = {}  # {"interactive": ["skinnywms", "folium"]}


full = []
for k, v in extras_require.items():
    full += v
full += install_requires

extras_require["full"] = full


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
    extras_require=extras_require,
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
    tests_require=[
        "pytest",
        "nbconvert",
        "jupyter",
        "pytest-cov",
        "climetlab-demo-dataset",
        "climetlab-demo-source",
    ],
    test_suite="tests",
)
