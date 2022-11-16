# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os
import re

import yaml

from climetlab.core.data import get_data_entry
from climetlab.utils.kwargs import merge_dicts

LOG = logging.getLogger(__name__)

CURRENT_DEPLOYS = []


def local():
    from dask.distributed import LocalCluster

    return LocalCluster


def ssh():
    from dask.distributed import SSHCluster

    return SSHCluster


def slurm():
    from dask_jobqueue import SLURMCluster

    return SLURMCluster


CLUSTERS = {
    "ssh": ssh,
    "SSHCluster": ssh,
    "local": local,
    "LocalCluster": local,
    "slurm": slurm,
    "SLURMCluster": slurm,
}


def resolve_cluster_name(name):
    return CLUSTERS[name]()


class DaskDeploy:
    _scale = None
    client = None

    def __init__(
        self,
        start_client=True,
        cluster_cls=None,
        cluster_kwargs=None,
        client_kwargs=None,
        scale=None,
    ):
        from dask.distributed import Client

        if cluster_kwargs is None:
            cluster_kwargs = {}
        if client_kwargs is None:
            client_kwargs = {}

        self.cluster = None
        self.client = None
        self._scale = scale

        self.cluster_class = resolve_cluster_name(cluster_cls)
        self.cluster_kwargs = cluster_kwargs
        LOG.debug(f"Creating Dask cluster: {self.cluster_class}({cluster_kwargs})")
        self.cluster = self.cluster_class(**self.cluster_kwargs)
        LOG.debug(f"Dask cluster={self.cluster}")

        self.scale()

        if start_client:
            self.client_kwargs = client_kwargs
            LOG.debug(f"Starting client: {client_kwargs}")
            self.client = Client(self.cluster, **self.client_kwargs)
            LOG.debug(f"Dask client={self.client}")

        CURRENT_DEPLOYS.append(self)

    def scale(self):
        if not self._scale:
            return
        print(f"Scaling to {self._scale}")
        self.cluster.scale(self._scale)

    def shutdown(self):
        if self.client:
            self.client.close()
        self.cluster.close()

    def __str__(self):
        return f"Cluster={self.cluster}, Client={self.client}"

    def _repr_html_(self):
        dashboard = self.cluster.dashboard_link
        dashboard = re.sub(
            "http://[0-9\\.]*:", "https://localhost:48167/proxy/", dashboard
        )
        return f"Cluster={self.cluster}, Client={self.client}, Dashboard:<a href='{dashboard}'>{dashboard}</a>"

    @property
    def dashboard_link(self):
        # TODO: make this work everywhere
        return self.cluster.dashboard_link


def start_dask(name_or_yaml_filename, **kwargs):

    if len(CURRENT_DEPLOYS) > 0:
        LOG.warn(
            f"Creating multiple dask clusters ({len(CURRENT_DEPLOYS)}) already running)."
        )

    _, ext = os.path.splitext(name_or_yaml_filename)
    if ext in (".yaml", ".yml"):
        # Explicit yaml file is provided
        filename = os.path.expanduser(name_or_yaml_filename)
        LOG.debug(f"Using yaml file {filename} to configure dask.")
        with open(filename) as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
    else:
        # The name (name_or_yaml_filename) refers to a yaml file in the climetlab//data
        # or user config ($HOME/.climetlab/dask).
        config = get_data_entry("dask", name=name_or_yaml_filename).data

    if "dask" in config:
        config = config["dask"]

    # kwargs always overwrite the config file values.
    config = merge_dicts(config, kwargs)

    LOG.debug(f"Creating a dask deployment with dask config {config}.")
    return DaskDeploy(**config)


def performance_report(*args, **kwargs):
    import dask.distributed

    return dask.distributed.performance_report(*args, **kwargs)
