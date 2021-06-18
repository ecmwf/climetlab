.. _datasets:

Datasets plugins
================

A :ref:`Dataset <datasets>` is a Python class that provide a curated
set of data with specific helper functions. CliMetLab has build-in
example datasets for demo purposes. See usage details in 
:doc:`Dataset (User guide) <../guide/datasets>` and implementation in
:doc:`Dataset (Dev guide) <../developer/datasets>`.
Dataset are added with pip plugin or yaml files.


.. _dataset-yaml:

Simple datasets using yaml files
--------------------------------


Simple datasets are datasets that rely on existing built-in :ref:`data
source <data-sources>`, and cannot be parametrised by users. This
can be for example a single file downloadable from a URL.


.. code-block:: yaml

  ---
  dataset:
    source: url
    args:
      url: http://download.ecmwf.int/test-data/metview/gallery/temp.bufr

    metadata:
      documentation: Sample BUFR file containing TEMP messages

.. _dataset-pip:

Complex datasets using pip plugin
---------------------------------

See https://github.com/ecmwf/climetlab-demo-dataset

.. code-block:: python
  :emphasize-lines: 6-8

    setuptools.setup(
        name="climetlab-demo-dataset",
        version="0.0.1",
        description="Example climetlab external dataset plugin",

        entry_points={"climetlab.datasets":
                ["demo-dataset = climetlab_demo_dataset:DemoDataset"]
        },

    )

See :ref:`CliMetLab plugin mechanism <plugins general>`.

See an `example notebook`_ using an external plugin.

Python documentation on plugins_.

Automatic generation of a pip package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make it easier, there is a `template for a Dataset plugin using cookiecutter
<https://github.com/ecmwf-lab/climetlab-cookiecutter-dataset>`_. In addition,
for a simple dataset, you can also use a yaml file and rely only on the code
provided by CliMetLab or other plugins.

.. code-block:: bash

    pip install cookiecutter
    cookiecutter https://github.com/ecmwf-lab/climetlab-cookiecutter/dataset



.. _example notebook: ../examples/12-external-plugins.ipynb

.. https://nbsphinx.readthedocs.io/en/0.7.1/a-normal-rst-file.html

.. _plugins: https://packaging.python.org/guides/creating-and-discovering-plugins/
