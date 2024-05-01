# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

from .tools import parse_args


class CompletionCmd:
    @parse_args(
        shell=(
            None,
            dict(
                metavar="SHELL",
                help="Shell to use for autocompletion. Must be zsh or bash.",
                nargs="?",
            ),
        ),
    )
    def do_completion(self, args):
        """
        Enable autocompletion for the "climetlab" shell command.

        Supported shells are : zsh bash.

        Usage:
            climetlab completion
        """
        from climetlab.scripts.main import command_list

        if not args.shell:
            return self.do_completion("--help")

        home = os.path.expanduser("~")

        def add_to_file(dotfile, lines):
            with open(dotfile, "a") as f:
                print(f"The following was added at the end of {dotfile} :\n")
                print("\n", file=f)
                for line in lines:
                    print(line, file=f)
                    print("  " + line)
                print("\nCompletion will be enabled for any new shell.")

        if args.shell == "zsh":
            # TODO: only add "fpath+= ( $HOME/.climetlab/autocomplete/zsh)"
            # and create the file $HOME/.climetlab/autocomplete/zsh/_climetlab)"
            dotfile = os.path.join(home, ".zshrc")
            lines = ["complete -W '" + " ".join(command_list()) + "' climetlab"]
            add_to_file(dotfile, lines)
            return

        if args.shell == "bash":
            dotfile = os.path.join(home, ".bashrc")
            lines = ["complete -W '" + " ".join(command_list()) + "' climetlab"]
            add_to_file(dotfile, lines)
            return

        raise NotImplementedError(f"Shell not supported: shell={args.shell}.")
