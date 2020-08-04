# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import os
from .base import FileSource
from climetlab.core.caching import temp_file
import requests
from tqdm import tqdm


class Url(FileSource):
    def __init__(self, url, **kwargs):

        super().__init__(**kwargs)

        _, extension = os.path.splitext(url)
        self.path = temp_file("Url", url, extension=extension)

        if not os.path.exists(self.path):
            print("Downloading", url)
            r = requests.head(url)
            r.raise_for_status()
            try:
                size = int(r.headers["content-length"])
            except Exception:
                size = None
            r = requests.get(url, stream=True)
            r.raise_for_status()
            total = 0
            mode = "wb"
            with tqdm(
                total=size,
                unit_scale=True,
                unit_divisor=1024,
                unit="B",
                disable=False,
                leave=False,
            ) as pbar:
                pbar.update(total)
                with open(self.path + ".tmp", mode) as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            total += len(chunk)
                            pbar.update(len(chunk))

            os.rename(self.path + ".tmp", self.path)


source = Url
