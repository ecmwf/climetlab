# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from climetlab import load_source
from climetlab.indexing import PerUrlIndex
from climetlab.sources.multi import MultiSource

from .prompt import APIKeyPrompt


class EODKeyPrompt(APIKeyPrompt):
    register_or_sign_in_url = "https://www.ecmwf.int/"
    retrieve_api_key_url = "https://www.ecmwf.int"

    prompts = [
        dict(
            name="url",
            default="c",
            title="API url",
            validate=r"http.?://.*",
        ),
    ]

    rcfile = "~/.ecmwf-open-data"


class EODRetriever(MultiSource):

    sphinxdoc = """
    EODRetriever
    """

    def __init__(self, *args, **kwargs):
        if len(args):
            assert len(args) == 1
            assert isinstance(args[0], dict)
            assert not kwargs
            kwargs = args[0]

        prompt = EODKeyPrompt()
        self.config = prompt.check(load=True)

        options = dict(
            url=self.config["url"],
            date=-1,
            step=0,
            resol="0p4",
            stream="oper",
            type="fc",
            extension=".grib2",
        )
        options.update(kwargs)
        # assert False, (kwargs, options)

        sources = self.requests(**options)

        super().__init__(sources)

    # @normalize("date", "date-list(%Y-%m-%d)")
    # @normalize("area", "bounding-box(list)")
    def requests(self, **request):

        for k, v in request.items():
            if not isinstance(v, (list, tuple)):
                request[k] = [v]

        pattern = (
            "{url}/{date:date(%Y%m%d)}/{date:date(%H)}z/{resol}/{stream}/"
            "{date:date(%Y%m%d%H%M%S)}-{step}h-{stream}-{type}{extension}"
        )

        index = PerUrlIndex(pattern, substitute_extension=True)

        # result = []
        # for p in Pattern(pattern).substitute([], **kwargs):
        #    result.append(load_source("url", p, lazily=True))# parts=[(0, 4)]))

        sources = load_source("indexed-urls", index, request)

        return sources


source = EODRetriever
