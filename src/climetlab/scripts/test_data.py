# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from .tools import parse_args


class TestDataCmd:
    @parse_args(
        directory=(
            None,
            dict(
                metavar="DIRECTORY",
                help="Shell to use for autocompletion. Must be zsh or bash.",
                nargs="?",
            ),
        ),
    )
    def do_test_data(self, args):
        """
        Create a directory with data used to test climetlab.

        """
        from climetlab.testing import build_testdata

        directory = args.directory
        if not directory:
            directory = "./test-data"

        print(f"Adding testdata in {directory}")
        build_testdata(directory)
        print(f"Added testdata in {directory}")
