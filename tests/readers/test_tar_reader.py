#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import mimetypes

from climetlab.testing import check_unsafe_archives


def test_tar_safety():
    check_unsafe_archives(".tar")


def test_tar_mimetypes():
    assert mimetypes.guess_type("x.tar") == ("application/x-tar", None)
    assert mimetypes.guess_type("x.tgz") == ("application/x-tar", "gzip")

    assert mimetypes.guess_type("x.tar.gz") == ("application/x-tar", "gzip")
    assert mimetypes.guess_type("x.tar.bz2") == ("application/x-tar", "bzip2")


if __name__ == "__main__":
    from climetlab.testing import main

    main(globals())
