# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


def download_and_cache(url: str) -> str:
    """[summary]

    :param url: [description]
    :type url: str
    :return: [description]
    :rtype: str
    """
    from climetlab import load_source

    return load_source("url", url).path


def bytes_to_string(n):
    u = ["", " KiB", " MiB", " GiB", " TiB", " PiB"]
    i = 0
    while n >= 1024:
        n /= 1024.0
        i += 1
    return "%g%s" % (int(n * 10 + 0.5) / 10.0, u[i])
