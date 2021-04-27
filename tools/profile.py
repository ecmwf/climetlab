#!/usr/bin/env python3
# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import random
import logging
import os
import shutil
import time
from tqdm import tqdm

from queue import Queue
from threading import Thread, Lock
import requests

import argparse

# from tqdm import tqdm

parser = argparse.ArgumentParser()

parser.add_argument(
    "-u",
    "--url",
    default="https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/training-input/ecmwf-hindcast/0.2.5/netcdf/ecmwf-hindcast-q-20200102.nc",
)
parser.add_argument("-t", "--threads", default=4, type=int)
parser.add_argument("-o", "--output", default="out.data", help="output file")
parser.add_argument("-b", "--buffer-size", type=int, default=1024)
parser.add_argument("-c", "--chunk-size", type=int, default=1024 * 1024 * 20)

args = parser.parse_args()


class Part:
    def __init__(self, start, length, url, write_lock, f, exception_list):
        self.start = start
        self.length = length
        self.url = url
        self.write_lock = write_lock
        self.f = f
        self.exception_list = exception_list

    def execute(self):
        try:
            self._execute()
        except Exception as e:
            with self.write_lock:
                self.exception_list.append(e)

    def _execute(self):
        end = self.start + self.length
        # headers = {'content-range':f'{self.start}-{end}/{self.size}'}
        headers = {"range": f"bytes={self.start}-{end}"}
        # print(f"downloading {headers} in {self.f}")
        r = requests.get(self.url, stream=True, headers=headers)  # , verify=False)
        r.raise_for_status()
        with self.write_lock:
            self.f.seek(self.start)
            for chunk in r.iter_content(chunk_size=args.buffer_size):
                if chunk:
                    self.f.write(chunk)


queue = Queue()


def worker():
    while True:
        time.sleep(0.1)
        part = queue.get()
        part.execute()
        queue.task_done()


for t in range(args.threads):
    Thread(target=worker, daemon=True).start()


def download(url, target):

    logging.info("Downloading %s", url)
    write_lock = Lock()
    download = target  # + ".download"
    mode = "wb"

    r = requests.head(url)  # , verify=False)
    r.raise_for_status()
    try:
        size = int(r.headers["content-length"])
    except Exception:
        size = None
        # TODO

    exception_list = []
    with open(download, mode) as f:
        total = 0
        chunk_size = args.chunk_size  # 20 * 1024 * 1024
        while total < size:
            chunk = min(size - total, chunk_size)
            queue.put(
                Part(
                    total,
                    chunk,
                    url,
                    write_lock=write_lock,
                    f=f,
                    exception_list=exception_list,
                )
            )
            total += chunk
        queue.join()
    if exception_list:
        print(exception_list)
        raise (exception_list[0])

    return size


if __name__ == "__main__":
    print(os.getpid())
    now = time.time()
    size = download(args.url, args.output)
    print(
        f"{size} downloaded at {size/(time.time() - now)/1024/1024}MB/s ({(time.time() - now)} sec)"
    )

# download(  'https://releases.ubuntu.com/20.04.2.0/ubuntu-20.04.2.0-desktop-amd64.iso', 'file.zip')
# download(  'https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input-dev/ecmwf-forecast/0.2.5/netcdf/ecmwf-forecast-q-20200102.nc', 'file.zip')
# download(
#    "https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/ecmwf-forecast/0.2.5/netcdf/ecmwf-forecast-ttr-20200102.nc",
#    "file.zip",
# )
# download( 'https://dataserv.ub.tum.de/s/m1524895/download?path=%2F5.625deg%2F2m_temperature&files=2m_temperature_5.625deg.zip', 'file.zip')
