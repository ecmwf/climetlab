# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#


from docutils import nodes
from docutils.parsers.rst import Directive


class SourcesDirective(Directive):
    def run(self):

        from climetlab.sources import list_entries

        return [nodes.paragraph(text=x) for x in list_entries()]


def setup(app):

    app.add_directive("sources", SourcesDirective)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
