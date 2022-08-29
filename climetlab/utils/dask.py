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

from climetlab.core.data import get_data_entries
from climetlab.core.settings import SETTINGS
from climetlab.utils.kwargs import Kwargs

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
    "local": local,
    "slurm": slurm,
}


def resolve_cluster_name(name):
    return CLUSTERS[name]()


class DaskDeploy:
    _scale = None
    client = None

    def __init__(
        self,
        start_client=True,
        kind=None,
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

        self.cluster_class = resolve_cluster_name(kind)
        self.cluster_kwargs = cluster_kwargs
        print(cluster_kwargs)
        self.cluster = self.cluster_class(**self.cluster_kwargs)
        print(f"Cluster= {self.cluster}")

        self.scale()

        if start_client:
            self.client_kwargs = client_kwargs
            print(client_kwargs)
            self.client = Client(self.cluster, **self.client_kwargs)
            print(f"Client= {self.client}")

    def scale(self):
        if not self._scale:
            return
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


def start(kind_or_yaml_filename='local', **kwargs):

    if len(CURRENT_DEPLOYS) > 0:
        warnings.warn(
            f"Creating multiple dask clusters ({len(CURRENT_DEPLOYS)}) already running)."
        )

    yaml_config = {}
    default_config = {}
    system_config = {}
    user_config = {}

    if kind_or_yaml_filename in CLUSTERS:
        kind = kind_or_yaml_filename
        yaml_config = {}
    else:
        with open(kind_or_yaml_filename) as f:
            yaml_config = yaml.load(f, loader=yaml.SafeLoader)['dask']
        kind = yaml_config['kind']

    try:
        configs = get_data_entries("dask", kind).as_list()
        if "user-settings" in [x.owner for x in configs]:
            user_config = [x.data for x in configs if x.owner='user-settings'][0]
        if "user-settings" in [x.owner for x in configs]:
            user_config = [x.data for x in configs if x.owner='user-settings'][0]
        print(user_config)
        print(default_config)
        default_config = default_config.data['dask']
    except KeyError:
        warnings.warn(f"Cannot load climetlab config for '{kind}'.")

    system_config_path = os.path.join("opt", "climetlab", "dask.yaml")
    if os.path.exists(system_config_path):
        with open(system_config_path) as f:
            system_config = yaml.load(f, loader=yaml.SafeLoader)['dask']
    
    print()
    print('default_config', default_config)
    print('system_config', system_config)
    print('yaml_config', yaml_config)

    deploy_kwargs = {}
    deep_update(deploy_kwargs, default_config)
    deep_update(deploy_kwargs, system_config)
    deep_update(deploy_kwargs, yaml_config)
    deep_update(deploy_kwargs, kwargs)

    print(deploy_kwargs)
    exit()
    deploy = DaskDeploy(**options)
    CURRENT_DEPLOYS.append(deploy)
    return deploy


def performance_report(*args, **kwargs):
    import dask.distributed

    return dask.distributed.performance_report(*args, **kwargs)
