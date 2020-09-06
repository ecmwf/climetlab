# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from docutils.parsers.rst import Directive
from docutils import statemachine
from importlib import import_module
from io import StringIO

# Examples at https://github.com/docutils-mirror/docutils


class ModuleOutput(Directive):

    has_content = True

    def run(self):

        self.assert_has_content()

        try:

            # Get current file
            current_rst_file = self.state_machine.input_lines.source(
                self.lineno - self.state_machine.input_offset - 1
            )

            name = [x for x in self.content if x != ""][0]

            module = import_module("..%s" % (name.replace("-", "_"),), package=__name__)

            out = StringIO()
            module.execute(out)
            out = out.getvalue()

            # Parse output
            rst_lines = statemachine.string2lines(out)
            # Insert in place
            self.state_machine.insert_input(rst_lines, current_rst_file)

        except Exception as e:
            rst_lines = statemachine.string2lines(str(e))
            self.state_machine.insert_input(rst_lines, current_rst_file)

        return []


def setup(app):
    app.add_directive("module-output", ModuleOutput)
