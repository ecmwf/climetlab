Howtos
======

TODO

NameError: Cannot find dataset 'XXX' (values are ...)
-----------------------------------------------------

When calling `cml.load_dataset('some-dataset'), I get this error.

Solution :

The dataset 'some-dataset-name' is not available, this could be due
to a typo in the dataset name (such as confusing 'some-dataset'
with 'somedataset').

If there is no typo, the relevant plugin providing the dataset may
not be installed.

.. code-block:: bash

   pip install climetlab-the-relevant-plugin

See the :ref:`list of plugins <plugin-list>`.

How to install climetlab ?
--------------------------

Solution :

.. code-block:: bash

   pip install climetlab

See the :ref:`installing instructions <installing>` for more details.

..
  .. command-output:: date +%Y%M%d

..
 .. command-output:: ls -l
