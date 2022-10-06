# flake8: noqa
import logging
import os
import time

import dask

import climetlab as cml

# https://github.com/dask/dask-jobqueue/issues/548
# http://localhost:8787/status


hosts = [f"node{i}" for i in range(0, 4)]

workers = list(i + 1 for i in range(len(hosts) - 1))

client = cml.start_dask(
    "ssh",
    cluster_kwargs=dict(
        hosts=hosts,
        connect_options=dict(
            config=os.path.expanduser("~/.ssh/vagrant_ssh_config"),
            known_hosts=None,
        ),
        remote_python="/usr/bin/python3",
        scheduler_options=dict(
            host="node0",
            port=9000,
            dashboard_address=":8787",
        ),
        # worker_options=dict(worker_port=[9000+i for i in workers])
    ),
).client


def inc(x):
    from distributed.worker import logger

    w = dask.distributed.get_worker()  # .log('hello')
    logger.info("xxxx", x)
    # assert False, type(w)
    return x + 1


x = client.submit(inc, 10)

print(client.get_events())
# print(client.scheduler.story())

time.sleep(10)

print(x.result())
