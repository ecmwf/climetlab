# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import ecmwf.opendata

from .file import FileSource


class EODRetriever(FileSource):

    sphinxdoc = """
    EODRetriever
    """

    def __init__(self, source="ecmwf", *args, **kwargs):
        if len(args):
            assert len(args) == 1
            assert isinstance(args[0], dict)
            assert not kwargs
            kwargs = args[0]

        self.source_kwargs = self.request(**kwargs)

        self.client = ecmwf.opendata.Client(source=source, preserve_request_order=True)

        self.path = self._retrieve(self.source_kwargs)

    def connect_to_mirror(self, mirror):
        return mirror.connection_for_eod(self)

    def _retrieve(self, request):
        def retrieve(target, request):
            self.client.retrieve(request, target)

        return self.cache_file(
            retrieve,
            request,
        )

    # @normalize("date", "date-list(%Y-%m-%d)")
    # @normalize("area", "bounding-box(list)")
    def request(self, **request):
        return request


source = EODRetriever
