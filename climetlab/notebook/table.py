# (C) Copyright 2021- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


class Table:
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.elements = {}

    def __setitem__(self, key, value):
        self.elements[key] = value

    def __getitem__(self, key):
        return self.elements[key]

    def _repr_html_(self):
        result = []
        result.append('<table style="padding:0;margin:0;">')
        for r in range(self.rows):
            result.append('<tr style="padding:0;margin:0;">')
            for c in range(self.columns):
                result.append('<td style="padding:0;margin:0;">')
                if (r, c) in self.elements:
                    result.append(self.render(self.elements[(r, c)]))
                else:
                    result.append("&nbsp;")
                result.append("</td>")
            result.append("</tr>")
        result.append("</table>")
        return "\n".join(str(s) for s in result)

    def render(self, element):
        e = element.render()
        src, attrs = e._repr_png_()
        return f'<img src="data:image/png;base64, {src}">'
