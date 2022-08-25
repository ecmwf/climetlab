# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from dask_jobqueue import SLURMCluster
import yaml

import climetlab as cml


class CustomSLURMCluster(SLURMCluster):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            cores=4,
            memory="8G",
            walltime="00:30:00",
            job_extra=[  # will be renamed job_extra_directives
                "--qos=np",
                "--cpus-per-task=256",
                "--ntasks=1",
            ],
            # scheduler_options={"dashboard_address": f":{portdash}"},
            **kwargs,
        )


def run_dask_cluster(yaml_filename=None, **kwargs):
    options = {}
    if yaml_filename is not None:
        with open(yaml_filename) as f:
            options.update(yaml.load(f))
    options.update(kwargs)

    kind = options.get("kind")

    if kind == "slurm":
        cluster = CustomSLURMCluster()
        cluster.scale(8)
        return cluster

    if kind == "local":
        from dask.distributed import LocalCluster

        cluster = LocalCluster()
        return cluster

    if kind == "ssh":
        from distributed import SSHCluster

        return SSHCluster(
            hosts=["localhost", "localhost", "localhost"],
            scheduler_options={"port": 12366},
        )

    raise ValueError(f"Unknown kind = {kind}")
