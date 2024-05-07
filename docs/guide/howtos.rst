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

How do I access data from this BUFR/GRIB/... file?
--------------------------------------------------

Use the :ref:`data-sources-file` source.

How do I access data from this file on this unsupported format?
---------------------------------------------------------------
Write your own python code to open the file.

.. todo::

   Add plugins and doc for readers.

How to help others to use my data ?
-----------------------------------
   Creating a CliMetLab plugin can be a solution to share some code along
   with the dataset that you are publishing/using.
   See the :ref:`plugin documentation <contributing-overview>`.


How to set up my CliMetLab cache directory ?
--------------------------------------------
   See :doc:`/guide/caching`.

How to share my cache directory with another user ?
---------------------------------------------------
   It is not recommended to share your cache with others.
   What you are looking for may be a mirror.
   And this feature is not implemented yet.

   A more robust approach is to put the data to a shared location,
   and define :doc:`a CliMetLab dataset </guide/datasets>` plugin to use it.

Can CliMetLab help using dask ?
-------------------------------
   See :doc:`/guide/dask`.
