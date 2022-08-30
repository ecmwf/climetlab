import os
import time

from dask.distributed import Client, LocalCluster, Worker, SSHCluster

import climetlab as cml

from climetlab.utils.dask import start

cluster = LocalCluster(n_workers=10, processes=False)
client = Client(cluster)

#start(kind='local',cluster_kwargs=dict(n_workers=10, processes=False))

#start('local-threads', n_workers=10)
#start('local-processes', n_workers=10, threads_per_worker=2)

import climetlab.debug
start('ssh', cluster_kwargs= dict(
    hosts = [f'node{i}' for i in range(0,3)],
    connect_options = dict(
        config = os.path.expanduser('~/.ssh/vagrant_ssh_config'),
        known_hosts = None,

    ),
    remote_python = '/usr/bin/python3',
))
#start('ssh', hosts = ['node1:23', 'node2:78'])


ds = cml.load_source("virtual", param="msl")
now = time.time()
print("a", len(ds), now)
x = ds.to_xarray()
print("b", time.time() - now)

y = x.msl
print(y.mean(dim="time").compute())
