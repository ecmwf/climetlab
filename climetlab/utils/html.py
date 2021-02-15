# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import re


def urlify(text):
    return re.sub(r"(https?://.*\S)", r'<a href="\1" target="_blank">\1</a>', text)


def css(name):
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "css", name)
    with open(path + ".css") as f:
        return "<style>%s</style>" % (f.read(),)


def table(obj):

    style = css("table")

    table = """
<h4>{name}</h4>
<table class="climetlab">
<tr><td><b>Home page</b></td><td>{home_page}</td></tr>
<tr><td><b>Documentation</b></td><td>{documentation}</td></tr>
<tr><td><b>Citation</b></td><td><pre>{citation}</pre></td></tr>
<tr><td><b>Licence</b></td><td>{licence}</td></tr>
</table>
        """.format(
        name=obj.name,
        home_page=urlify(obj.home_page),
        licence=urlify(obj.licence),
        citation=obj.citation,
        documentation=urlify(obj.documentation),
    )

    return style + table
