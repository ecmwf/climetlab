Using dask
==========


Climetlab dask tools
--------------------

You do not need CliMetLab to use `dask`. Dask is an independent python package often use with.
to `xarray` and `pandas`. As CliMetLab seeks a strong integration to `dask`, some high-level
functions may be useful to ease the interaction with dask.

.. todo::

   This whole part about dask is EXPERIMENTAL, it will change in the future, may be removed or
   (very likely) moved to another package.


Start an local cluster and client
*********************************

.. code-block:: python

   from climetlab.utils.dask import start
   start('local')
   # or $ climetlab dask start local
   # or $ climetlab dask local --start

Start an ssh cluster and client
*******************************

.. code-block:: python

   from climetlab.utils.dask import start
   start('ssh')


Start a SLURM dask cluster and client
*************************************

.. code-block:: python

   from climetlab.utils.dask import start
   start('slurm')


Start a slurm dask cluster on HPC
*********************************

.. note::
This is assumes that your HPC admin set up the hpc-name-config-1.yaml file on the appropriate location.

.. code-block:: python

   from climetlab.utils.dask import start
   start('hpc-name-config-1')


Access the dask dashboard
*************************

.. todo::
   Not implemented yet.

Access the dask logs
********************

.. todo::
   Not implemented yet.

Stop the dask cluster
*********************

The dask cluster and client will usually stop automatically when the python process ends.
Nevertheless, it is possible to stop dask if it has been started from climetlab.

.. code-block:: python

   from climetlab.utils.dask import stop
   stop()

Advanced dask usages
--------------------

Note: In this section a "dask deployement" refers to a client and a cluster.
It does not refers to a Cloud deployement using Kubernetes, etc.

Create a custom dask deployement specifications
***********************************************

Create the yaml file $HOME/.climetlab/dask/hpc-name-config-1.yaml. Then use it with:

.. code-block:: python

   from climetlab.utils.dask import start
   start('hpc-name-config-1')

.. todo::

   This is EXPERIMENTAL.

.. note::

   For HPC system admin:
   Adding yaml files in /opt/climetlab/dask/*.yaml will give global access to all users.


Reuse the dask client
*********************

.. code-block:: python

   from climetlab.utils.dask import start
   client = start('local').client


Scale the dask cluster
**********************

.. todo::

   Define what "scale" mean in this context.


.. code-block:: python

   from climetlab.utils.dask import start
   deploy = start('slurm')
   deploy.scale(..)
