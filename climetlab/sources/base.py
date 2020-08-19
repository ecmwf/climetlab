# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from . import DataSource
from .readers import reader
import getpass
import sys
import os
import markdown
import re

ipython = False
try:
    from IPython.display import display
    from IPython.display import HTML

    ipython = True
except Exception:
    pass


class FileSource(DataSource):

    _reader_ = None

    @property
    def _reader(self):
        if self._reader_ is None:
            self._reader_ = reader(self, self.path)
        return self._reader_

    def __iter__(self):
        return iter(self._reader)

    def __len__(self):
        return len(self._reader)

    def __getitem__(self, n):
        return self._reader[n]

    def to_xarray(self, *args, **kwargs):
        return self._reader.to_xarray(*args, **kwargs)

    def to_pandas(self, *args, **kwargs):
        return self._reader.to_pandas(*args, **kwargs)

    def to_numpy(self, *args, **kwargs):
        return self._reader.to_numpy(*args, **kwargs)

    def to_metview(self, *args, **kwargs):
        return self._reader.to_metview(*args, **kwargs)


# See https://medium.com/analytics-vidhya/the-ultimate-markdown-guide-for-jupyter-notebook-d5e5abf728fd
HTML_MESSAGE = """
<div style='border: 1px solid orange; color: black; background-color: rgb(255, 214, 0); margin: 0.5em; padding: 0.5em; font-weight: bold;'>
{message}
</div>
"""


class APIKeyPrompt:
    def ask_user_and_save(self):
        if ipython:
            text = self.ask_user_markdown()
        else:
            text = self.ask_user_text()

        try:
            text = self.validate(text)
        except Exception as e:
            print("Invalid API key: %s" % (e,), file=sys.stderr)
            return False

        rcfile = os.path.expanduser(self.rcfile)
        with open(rcfile, "w") as f:
            print(text, file=f)

        print("API key saved to '%s'" % (rcfile,), file=sys.stderr)

        return True

    def ask_user_text(self):
        print(self.text_message, file=sys.stderr)
        return getpass.getpass(self.prompt + ": ")

    def ask_user_markdown(self):
        message = markdown.markdown(self.markdown_message)
        # We use Python's markdown instead of IPython's Markdown because
        # jupyter lab/colab/deepnotes all behave differently
        display(HTML(HTML_MESSAGE.format(message=message)))
        return getpass.getpass(self.prompt + ": ")
