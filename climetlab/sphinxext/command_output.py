import os
import subprocess

from docutils.parsers.rst import Directive
from docutils import statemachine
from shlex import split


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

        except Exception as e:
            rst_lines = statemachine.string2lines(str(e))
            self.state_machine.insert_input(rst_lines, current_rst_file)

        finally:
            os.chdir(here)

        return []


def setup(app):
    app.add_directive("command-output", CommandOutput)
