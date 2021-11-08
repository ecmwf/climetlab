# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from xml.dom import minidom

from climetlab.utils import download_and_cache

URL = "https://cfconventions.org/Data/cf-standard-names/{version}/src/cf-standard-name-table.xml"


def cf_standard_names(version=78):
    path = download_and_cache(URL.format(version=version))
    xmldoc = minidom.parse(path)
    entries = xmldoc.getElementsByTagName("entry")
    for entry in entries:
        yield entry.attributes["id"].value


if __name__ == "__main__":

    for n in cf_standard_names():
        print(n)
