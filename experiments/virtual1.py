import os
import time
import climetlab as cml
import climetlab.debug  # noqa
from climetlab.utils.dask import start

# http://localhost:8787/status

start(
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
        ),
    ),
)
ds = cml.load_source("virtual", param="msl")
now = time.time()
print("a", len(ds), now)
x = ds.to_xarray()
print("b", time.time() - now)

y = x.msl
print(y.mean(dim="time").compute())
