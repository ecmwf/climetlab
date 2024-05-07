.. _datasets-plugins:

.. _dataset-pip:

How to create a dataset plugin (pip)
====================================

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

  **Naming convention**

  - A plugin package name (pip) should preferably start with ``climetlab-``
    and use dashes "-".
  - The Python package to import should start with
    :py:class:`climetlab\_` and must use underscores "_".
  - A CliMetLab dataset defined by a plugin should start with
    the plugin name and must use dashes "-".

Blueprint
~~~~~~~~~

Automatic creation script
-------------------------

While creating the package manually from the documentation and from
the example above is possible, there is also a semi-automated way
to generate a pip package from a template. The generated package
has a predefined dataset and is ready to be shared on Github and
distributed with pip.

.. code-block:: bash

    $ pip install climetlab-plugin-tools
    $ climetlab plugin_create_dataset
    # Answer the questions
    # Only the first question (plugin name) and the latest (licence) are required.
    # Other have sensible default values.

Here is a `verbose output of running the plugin creation script <https://raw.githubusercontent.com/ecmwf-lab/climetlab-plugin-tools/main/tests/dataset/generic/test_dataset_for_doc.stdout>`_.


.. note::

  **"Unknown command plugin_create_dataset"** This error
  happens if you have not installed the package `climetlab-plugin-tools`.

    .. code-block:: bash

      $ climetlab plugin_create_dataset
      Unknown command plugin_create_dataset. Type help for the list of known command names.

Dataset names
-------------

The plugin mechanism relies on using `entry_points`.
The three lines highlighted below
are registering the class `climetlab_dataset_plugin.rain_observations:RainObservations`
with `entry_points` to a CliMetLab dataset called  ``dataset-plugin-rain-observations``.
The python plugin mechanism is exhaustively described in the
`Python reference documentation <https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/>`_
and here are more details about :ref:`how on CliMetLab uses it<plugins-reference>`.

.. code-block:: python
  :emphasize-lines: 6-8

  setuptools.setup(
   name="climetlab-dataset-plugin",
   version="0.0.1",
   description="Example climetlab external dataset plugin",

   entry_points={"climetlab.datasets":
    ["dataset-plugin-rain-observations=climetlab_dataset_plugin.rain_observations:RainObservations"]
   },

  )

Once `entry_point` has registered the class, the end-user can use this external plugin to access it

.. code-block:: python

  import climetlab as cml
  cml.load_dataset("dataset-plugin-rain-observations")


Automatic testing of the plugin
-------------------------------

In the folder ``tests`` are set up automatic tests of the plugin using pytest.
If the repository is hosted on github, the tests triggers automatically when pushing to the repository.
Additionally, code quality is enabled using black, isort and flake.

All tests could be disabled or adapted in the ``.github/workflows/`` folder.

Notebooks as documentation
--------------------------

The folder ``notebooks`` in each plugin can be used to store usage example
or demo on how to use the data, such as this `notebook <https://github.com/ecmwf-lab/climetlab-plugin-tools/blob/main/tests/dataset/generic/climetlab-dataset-plugin.ref/notebooks/demo_rain_observations.ipynb>`_,
Notebook are automatically tested if the repository is on github.

Links on the README file are pointing to binder, colab, etc. to run the automatically created notebook.

Manually creating the Python package
------------------------------------

Here is a minimal example of pip package defining a dataset plugin :
https://github.com/ecmwf/climetlab-demo-dataset


Adapting plugin code
~~~~~~~~~~~~~~~~~~~~

Renaming a dataset
------------------

The dataset name can be changed by changing the ``setup.py`` file.

.. code-block:: python

   - ["dataset-plugin-rain-observations=climetlab_dataset_plugin.rain_observations:RainObservations"]
   + ["dataset-plugin-new-name         =climetlab_dataset_plugin.rain_observations:RainObservations"]

A good practice is to change keep the class name in sync with the dataset name.


Adding a dataset to a plugin
----------------------------

New datasets can be added to the plugin, as long as the corresponding class is created:

.. code-block:: python

   - ["dataset-plugin-rain-observations=climetlab_dataset_plugin.rain_observations:RainObservations"]
   + ["dataset-plugin-rain-observations=climetlab_dataset_plugin.rain_observations:RainObservations",
   +  "dataset-plugin-rain-forecast    =climetlab_dataset_plugin.rain_observations:RainForecast"]


CliMetLab hooks
---------------

.. todo::

  Document .source attribute, to_xarray(), to_pandas(), to_etc()
  Point to decorator
