Howtos
======

How to install CliMetLab?
-------------------------
   .. code-block:: bash

      pip install climetlab

   See the :ref:`installing instructions <installing>` for more details.

How to access data?
-------------------
   There are two ways to access data using CliMetLab:

   - :doc:`Using a Dataset </guide/datasets>`:
     CliMetLab provides a few demo datasets.
     In order to access other datasets with :py:func:`cml.load_dataset`,
     the relevant plugin must be installed.

   - :doc:`Using a data Source </guide/sources>`:
     A data Source allows loading various kinds of data format and location through
     :py:func:`cml.load_source`. Data sources should be used when there is no dataset
     plugin for the data you are interested in.

How to help others to use my data ?
-----------------------------------
   Creating a CliMetLab plugin can be a solution to share some code along
   with the dataset that you are publishing/using.
   See the :ref:`plugin documentation <contributing-overview>`.


How to set up my cache directory ?
----------------------------------
   See :doc:`/guide/caching`.

How to share my cache directory with another user ?
---------------------------------------------------
   It is not recommended to share your cache with others.
   What you are looking for may be a mirror.
   This feature is not implemented yet.

Climetlab dask tools
--------------------

Start an local cluster and client
*********************************

from climetlab.utils.dask import start
start('local')
# or $ climetlab dask start local
# or $ climetlab dask local --start

Start an ssh cluster and client
*******************************

from climetlab.utils.dask import start
start('ssh')


Start a SLURM dask cluster and client
*************************************

from climetlab.utils.dask import start
start('slurm')


Start a slurm dask cluster on HPC
*********************************

.. note::
This is assumes that your HPC admin set up the hpc-name-config-1.yaml file on the appropriate location.

from climetlab.utils.dask import start
start('hpc-name-config-1')



Access the dask dashboard
*************************

.. todo::
   todo

Access the dask logs
********************

.. todo::
   todo

Stop the dask cluster 
*********************

The dask cluster and client will usually stop automatically when the python process ends.
Nevertheless, it is possible to stop dask if it has been started from climetlab.

from climetlab.utils.dask import stop
stop()

Advanced dask usages
--------------------

Note: In this section a "dask deployement" refers to a client and a cluster. It does not refers to a Cloud deployement using Kubernetes, etc.

Create a custom dask deployement specifications
***********************************************

Create the yaml file $HOME/.climetlab/dask/hpc-name-config-1.yaml. Then use it with:
from climetlab.utils.dask import start
start('hpc-name-config-1')

.. note::

   For HPC system admin:
   Adding yaml files in /opt/climetlab/dask/*.yaml will give global access to all users. 


Reuse the dask client
*********************

from climetlab.utils.dask import start
client = start('local').client


Scale the dask cluster
**********************

from climetlab.utils.dask import start
deploy = start('slurm')
deploy.scale(..)