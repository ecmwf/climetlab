# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import getpass
import logging
import os
from abc import ABC, abstractmethod

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


class APIKeyPrompt(ABC):
    def ask_user_and_save(self):
        if ipython_active:
            text = self.ask_user_markdown()
        else:
            text = self.ask_user_text()

        try:
            text = self.validate(text)
        except Exception:
            LOG.error("Invalid API key", exc_info=True)
            return False

        rcfile = os.path.expanduser(self.rcfile)
        with open(rcfile, "w") as f:
            print(text, file=f)

        LOG.info("API key saved to '%s'", rcfile)

        return True

    def ask_user_text(self) -> str:
        return getpass.getpass("\n".join([self.text_message, self.prompt + ": "]))

    def ask_user_markdown(self) -> str:
        message = markdown.markdown(self.markdown_message)
        # We use Python's markdown instead of IPython's Markdown because
        # jupyter lab/colab/deepnotes all behave differently
        display(HTML(HTML_MESSAGE.format(message=message)))
        return getpass.getpass(self.prompt + ": ")

    @abstractmethod
    def prompt(self):
        pass

    @abstractmethod
    def validate(self, text):
        pass

    @abstractmethod
    def rcfile(self, text):
        pass

    @abstractmethod
    def text_message(self):
        pass

    @abstractmethod
    def markdown_message(self):
        pass
