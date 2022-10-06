#!/user/bin/env python3
# flake8: noqa

import sys
import time

import climetlab as cml
from climetlab.utils.dask import start


def main():
    if len(sys.argv) > 1:
        kind = sys.argv[1]
        deploy = start(kind, start_client=False)
    else:
        deploy = start(start_client=False)
    print(f"Running dask server {deploy}")
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
