Howtos
======

How to install CliMetLab?
-------------------------
   .. code-block:: bash

      pip install climetlab

   See the :ref:`installing instructions <installing>` for more details.

How to access data?
-------------------
   CliMetLab only provides a few demo datasets.
   In order to access a dataset with :py:func:`cml.load_dataset`,
   the relevant plugin must be installed (:doc:`details </guide/datasets>`).

   If there is no plugin for the data you are interested in,
   use :py:func:`cml.load_source` (:doc:`details </guide/sources>`).

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

.. todo::

  Add more standard recipes.
