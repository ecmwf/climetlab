# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import subprocess
import traceback
from shlex import split

from docutils import statemachine
from docutils.parsers.rst import Directive

# Examples at https://github.com/docutils-mirror/docutils


class CommandOutput(Directive):

    has_content = True

    def run(self):

        self.assert_has_content()

        here = os.getcwd()

        try:

            # Get current file
            current_rst_file = self.state_machine.input_lines.source(
                self.lineno - self.state_machine.input_offset - 1
            )

            os.chdir(os.path.dirname(current_rst_file))

            cmd = [x for x in self.content if x != ""][0]

            out = subprocess.check_output(split(cmd)).decode("utf-8")

            # Parse output
            rst_lines = statemachine.string2lines(out)
            # Insert in place
            self.state_machine.insert_input(rst_lines, current_rst_file)

        except Exception:
            # rst_lines = statemachine.string2lines(str(e))
            rst_lines = statemachine.string2lines(traceback.format_exc())
            self.state_machine.insert_input(rst_lines, current_rst_file)

        finally:
            os.chdir(here)

        return []


def setup(app):
    app.add_directive("command-output", CommandOutput)
