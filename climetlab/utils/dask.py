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
import warnings

import yaml

from climetlab.core.data import get_data_entry
from climetlab.core.settings import SETTINGS
from climetlab.utils.kwargs import Kwargs, merge_dicts

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
        print("Creating cluster: ", self.cluster_class, cluster_kwargs)
        self.cluster = self.cluster_class(**self.cluster_kwargs)
        print(f"Cluster= {self.cluster}")

        self.scale()

        if start_client:
            self.client_kwargs = client_kwargs
            print(client_kwargs)
            self.client = Client(self.cluster, **self.client_kwargs)
            print(f"Client= {self.client}")

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


def stop():
    while len(CURRENT_DEPLOYS):
        deploy = CURRENT_DEPLOYS.pop()  # TODO: make this CURRENT_DEPLOYS thread safe?
        deploy.shutdown()


###########################
# def start(yaml_filename=None, kind=None, **kwargs):
#    cml.dask.start_ssh() ?
#    cml.dask.start()   --> use system default? depend on .climetlab/setting.yaml:dask ?
#    cml.dask.start(...)
#    cml.dask.start('ssh', ...)
#    cml.dask.start('./ssh.yaml', ...) --> overwrite config? merge?
# cml.dask.start('atos-ssh')
# cml.dask.start('atos-slurm-2-nodes', cluster_kwargs={...})
# cml.dask.start('atos-slurm-20-nodes')
###########################


# TODO: reuse cml.utils.Kwargs
def deep_update(old, new):
    # deep update, merging dictionaries
    assert isinstance(new, dict), f"Expecting a dict, but received: {new}"
    for k, v in new.items():
        if k in old and isinstance(old[k], dict):
            deep_update(old[k], v)
        old[k] = v
    return old


def start(name_or_yaml_filename, **kwargs):

    if len(CURRENT_DEPLOYS) > 0:
        warnings.warn(
            f"Creating multiple dask clusters ({len(CURRENT_DEPLOYS)}) already running)."
        )

    _, ext = os.path.splitext(name_or_yaml_filename)
    if ext in (".yaml", ".yml"):
        # system_config_path = os.path.join(
        #     "opt", "climetlab", "dask", f"{name_or_yaml_filename}"
        # )
        filename = os.path.expanduser(name_or_yaml_filename)
        # if os.path.exists(name_or_yaml_filename):
        # The name (name_or_yaml_filename) IS a yaml file.
        # pass
        # elif os.path.exists(system_config_path):
        #    # The name (name_or_yaml_filename) is refering to a system config file
        #    # TODO: move system config into get_data_entry ?
        #    filename = system_config_path

        LOG.debug(f"Using yaml file {filename} to configure dask.")
        with open(filename) as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

    else:
        # The name (name_or_yaml_filename) refers to a yaml file in the climetlab//data or user config ($HOME/.climetlab/dask).
        config = get_data_entry(
            "dask",
            name=name_or_yaml_filename,
            merge=True,
        )
        print(config)
        LOG.debug(f"Built config for dask {config}.")

    if "dask" in config:
        config = config["dask"]

    # kwargs always overwrite the config file values.
    config = merge_dicts(config, kwargs)

    return DaskDeploy(**config)


def performance_report(*args, **kwargs):
    import dask.distributed

    return dask.distributed.performance_report(*args, **kwargs)
