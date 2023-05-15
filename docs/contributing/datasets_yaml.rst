.. _dataset-yaml:

How to create a dataset plugin (YAML)
-------------------------------------

YAML file definitions can be used for simple datasets which rely on
existing built-in :ref:`data source <data-sources>`, and cannot be
as flexible to end-users. The following example shows how to use a
source when the data consists of a single file downloadable from a URL.

.. code-block:: yaml

  ---
  dataset:
    source: url
    args:
      url: http://get.ecmwf.int/test-data/metview/gallery/temp.bufr

    metadata:
      documentation: Sample BUFR file containing TEMP messages


.. todo::
  Document the YAML file way to create a dataset.
  Choose a good way to implement the workflow.

 - Create a dataset YAML file.
 - Distribute it.
