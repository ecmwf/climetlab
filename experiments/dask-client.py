import os
import time

import climetlab as cml

# https://github.com/dask/dask-jobqueue/issues/548
# http://localhost:8787/status

client = cml.start_dask(
    "ssh",
    cluster_kwargs=dict(
        hosts=[f"node{i}" for i in range(0, 3)],
        connect_options=dict(
            config=os.path.expanduser("~/.ssh/vagrant_ssh_config"),
            known_hosts=None,
        ),
        remote_python="/usr/bin/python3",
        scheduler_options=dict(
            host="localhost",
            port=8786,
            dashboard_address=":8787",
        ),
    ),
).client


def inc(x):
    return x + 1


x = client.submit(inc, 10)
print(x.result())
