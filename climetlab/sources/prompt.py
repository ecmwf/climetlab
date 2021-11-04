# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import logging
import os
import re
import stat
from getpass import getpass

import markdown

from climetlab.core.ipython import HTML, display, ipython_active

LOG = logging.getLogger(__name__)


# See https://medium.com/analytics-vidhya/the-ultimate-markdown-guide-for-jupyter-notebook-d5e5abf728fd
HTML_MESSAGE = """
<div style='border: 1px solid orange; color: black;
     background-color: rgb(255, 214, 0);
     margin: 0.5em; padding: 0.5em; font-weight: bold;'>
{message}
</div>
"""

HTML_ASK = """
<div style='border: 1px solid gray; color: black;
     background-color: rgb(230, 230, 230);
     margin: 0.2em; padding: 0.2em; font-weight: bold;'>
{message}
</div>
"""

MESSAGE = """
An API key is needed to access this dataset. Please visit
{register_or_sign_in_url} to register or sign-in
then visit {retrieve_api_key_url} to retrieve you API key.
"""


class RegexValidate:
    def __init__(self, pattern):
        self.pattern = pattern

    def __call__(self, value):
        assert re.fullmatch(self.pattern, value), (self.pattern, value)
        return value


class Prompt:
    def __init__(self, owner):
        self.owner = owner

    def ask_user(self):

        self.print_message()

        result = {}

        for p in self.owner.prompts:
            method = getpass if p.get("hidden", False) else input
            value = self.ask(p, method)
            value = value.strip() or p.get("default", "")

            validate = p.get("validate")
            if validate:
                if isinstance(validate, str):
                    validate = RegexValidate(validate)

                value = validate(value)

            result[p["name"]] = value

        return result


class Text(Prompt):
    def print_message(self):
        print(
            MESSAGE.format(
                register_or_sign_in_url=self.owner.register_or_sign_in_url,
                retrieve_api_key_url=self.owner.retrieve_api_key_url,
            )
        )

    def ask(self, p, method):
        message = f"Please enter a value for '{p.get('title')}'"
        if "default" in p:
            message += f" or leave empty for the default value '{p.get('default')}'"
        message += ", then press <ENTER>"
        return method(p.get("title") + ": ").strip()


class Markdown(Prompt):
    def print_message(self):
        message = markdown.markdown(
            MESSAGE.format(
                register_or_sign_in_url=f"<{self.owner.register_or_sign_in_url}>",
                retrieve_api_key_url=f"<{self.owner.retrieve_api_key_url}>",
            )
        )
        # We use Python's markdown instead of IPython's Markdown because
        # jupyter lab/colab/deepnotes all behave differently
        display(HTML(HTML_MESSAGE.format(message=message)))

    def ask(self, p, method):
        message = f"Please enter a value for <span style='color: red;'>{p.get('title')}</span>"
        if "default" in p:
            message += f" or leave empty for the default value <span style='color: red;'>{p.get('default')}</span>"
        message += ", then press *ENTER*"
        if "example" in p:
            message += f" The value should look like  <span style='color: red;'>{p.get('example')}</span>"
        message = markdown.markdown(message)
        display(HTML(HTML_ASK.format(message=message)))
        return method(p.get("title") + ": ").strip()


class APIKeyPrompt:
    def check(self, load=False):
        rcfile = os.path.expanduser(self.rcfile)
        if not os.path.exists(rcfile):
            self.ask_user_and_save()

        if load:
            with open(rcfile) as f:
                return self.load(f)

    def ask_user(self):
        if ipython_active:
            prompt = Markdown(self)
        else:
            prompt = Text(self)

        return self.validate(prompt.ask_user())

    def ask_user_and_save(self):

        input = self.ask_user()

        rcfile = os.path.expanduser(self.rcfile)
        with open(rcfile, "w") as f:
            self.save(input, f)

        LOG.info("API key saved to '%s'", rcfile)

        try:
            os.chmod(rcfile, stat.S_IREAD | stat.S_IWRITE)
        except OSError:
            LOG.exception("Cannot change access to rcfile")

        return input

    def save(self, input, file):
        json.dump(input, file, indent=4)

    def load(self, file):
        return json.load(file)

    def validate(self, input):
        return input
