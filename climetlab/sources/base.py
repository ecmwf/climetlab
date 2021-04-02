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

from ..readers import reader
from . import Source

LOG = logging.getLogger(__name__)


class FileSource(Source):

    _reader_ = None
    path = None

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

    def sel(self, *args, **kwargs):
        return self._reader.sel(*args, **kwargs)

    def to_xarray(self, *args, **kwargs):
        return self._reader.to_xarray(*args, **kwargs)

    def to_pandas(self, *args, **kwargs):
        return self._reader.to_pandas(*args, **kwargs)

    def to_numpy(self, *args, **kwargs):
        return self._reader.to_numpy(*args, **kwargs)

    def to_metview(self, *args, **kwargs):
        return self._reader.to_metview(*args, **kwargs)

    def multi_merge(sources):
        f = FileSource()
        t = type(sources[0]._reader)
        assert all(type(s._reader) == t for s in sources)
        f._reader_ = t.multi_merge(f, [a._reader for a in sources])
        return os.fspath

    def _attributes(self, names):
        return self._reader._attributes(names)


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
