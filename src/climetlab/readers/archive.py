# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os

from climetlab.utils import tqdm

from . import Reader
from . import reader as find_reader

LOG = logging.getLogger(__name__)


class ArchiveReader(Reader):
    def __init__(self, source, path):
        super().__init__(source, path)

    def check(self, member):
        # A bit of paranoia

        if not member.isdir() and not member.isfile():
            LOG.warning(
                "Ignoring archive member '%s' because it is not a directory or a file",
                member.name,
            )
            return False

        if member.name.startswith("/"):
            LOG.warning(
                "Ignoring archive member '%s' because it is a full path",
                member.name,
            )
            return False

        if ".." in member.name:
            LOG.warning(
                "Ignoring archive member '%s' because contains '..'",
                member.name,
            )
            return False

        return True

    def mutate(self):
        if os.path.isdir(self.path):
            return find_reader(self.source, self.path).mutate()

        return self

    def expand(self, archive, members, **kwargs):
        def unpack(target, args):
            try:
                os.mkdir(target)
            except FileExistsError:
                pass

            for member in tqdm(iterable=members, total=len(members), leave=False):
                if not self.check(member):
                    continue
                archive.extract(member=member, path=target, **kwargs)

        self.path = self.cache_file(
            unpack,
            self.path,
            extension=".d",
            replace=self.path,
        )
