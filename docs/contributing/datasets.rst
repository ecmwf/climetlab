.. _datasets-plugins:

How to create a dataset plugin
==============================

:doc:`From the end-user's perspective <../guide/datasets>`, a **Dataset**
is a object created using ``cml.load_dataset(name, *args)`` with
the appropriate name and arguments, which provides data.

From the plugin's developer perspective, a **Dataset** is a Python class
that inherits from the CliMetLab class ``climetlab.Dataset``. This class
contains the Python code providing specific helper functions
and curated access to the data. Dataset can also be defined
from :ref:`yaml files <dataset-yaml>` if they have no specific
Python code and rely on (yet to defined) standard conventions.

CliMetLab has build-in example datasets for demo purposes.
And more examples can be found in the non-exhaustive
:doc:`list of CliMetLab plugins <../guide/pluginlist>`.

.. note::

  **Naming convention**: A plugin package name should preferably starts with ``climetlab-`` and use "-". The Python package to import should starts with
  :py:class:`climetlab\_` and use "_".


.. _dataset-pip:

With a Python package
---------------------

Here is a minimal example of pip package defining a dataset plugin :
https://github.com/ecmwf/climetlab-demo-dataset

The plugin mechanism relies on using `entry_points`.
The three lines highlighted below
are registering the class `climetlab_demo_dataset.DemoDataset`
with entry_points. Then as seen in the `example notebook`_,
the end-user can use this external plugin to access the class
``cml.load_dataset("demo-dataset")``.

This is exhaustively described in the
`Python reference documentation <https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/>`_
and here are more details about
:ref:`how on CliMetLab uses it<plugins-reference>`.

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


With a Python package (automated)
---------------------------------

While creating the package manually from the documentation and from
the example above is possible, there is also a semi-automated way relying
on `cookiecutter <https://cookiecutter.readthedocs.io/en/latest/>`_
to generate a pip package from a template. The generated package
has a predefined dataset and is ready to be shared on Github and
distributed.


For detailed information, please see the `README file <https://github.com/ecmwf-lab/climetlab-cookiecutter-dataset/blob/main/README.md>`_).

.. code-block:: bash

    pip install cookiecutter
    cookiecutter https://github.com/ecmwf-lab/climetlab-cookiecutter/dataset



.. _example notebook: ../examples/12-external-plugins.ipynb

.. https://nbsphinx.readthedocs.io/en/0.7.1/a-normal-rst-file.html

.. _dataset-yaml:

With a YAML file
----------------

YAML file definitions can be used for simple datasets which rely on
existing built-in :ref:`data source <data-sources>`, and cannot be
as flexible to end-users. The following example shows how to use a
source when the data consists of a single file downloadable from a URL.

.. code-block:: yaml

  ---
  dataset:
    source: url
    args:
      url: http://download.ecmwf.int/test-data/metview/gallery/temp.bufr

    metadata:
      documentation: Sample BUFR file containing TEMP messages


.. todo::
  Document the YAML file way to create a dataset.
  Choose a good way to implement the workflow.

 - Create a dataset YAML file.
 - distribute it.
