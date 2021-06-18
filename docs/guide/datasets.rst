.. _datasets:

Datasets
========

A ``Dataset`` is a Python class providing a curated set of data with specific helper functions.

When working on data, we are often writing code to transform, preprocess, adapt the data to our needs.
While it may be very nice to understand deeply to deep magic under the hood, this process could very time consuming.
Once somebody else did the hard work of preparing the data for a given purpose and designing relevant functions to process it,
their code can be integrated into a dataset plugin and made available to others through a CliMetLab plugin. 

CliMetLab has build-in datasets (as examples) and most of the datasets are available as plugins.

.. _accessing_data:

Accessing data in a dataset
---------------------------

First, the relevant plugin has been installed, generally using pip

    .. code-block:: bash

        pip install --quiet climetlab-demo-dataset

Second, the dataset can be loaded with :py:func:`load_dataset()` as follows:

    .. code-block:: python

        >>> import climetlab as cml
        >>> ds = cml.load_dataset("demo-dataset")

Notice that the relevant plugin package **must be installed** to access the
dataset, with pip (such as ``pip install climetlab-demo-dataset``).
If the package is not installed, CliMetLab will fail with a NameError
exception.

    .. code-block:: python

        >>> ds = climetlab.load_dataset("demo-dataset")
        NameError: Cannot find dataset 'demo-dataset' (values are ...),


When dataset ``some-dataset`` appears to be unavailable, this could be
due to a typo in the dataset name (such as confusing ``some-dataset``
with ``somedataset``).

.. note::
    When sharing a python notebook, it is a good practice to add
    ``!pip install climetlab-...`` at the top of the notebook.

The plugin name does not have to match the dataset name, and one plugin
usually provides several datasets.
As an example, the plugin ``climetlab_s2s_ai_challenge`` provides
the datasets ``s2s-ai-challenge-training-input`` and ``s2s-ai-challenge-training-output``:

.. code-block:: ipython

    >>> !pip install climetlab_s2s_ai_challenge
    >>> climetlab.load_dataset("s2s-ai-challenge-training-input")
    >>> climetlab.load_dataset("s2s-ai-challenge-training-output")


There is no need to import the plugin package to enable load the dataset:

.. code-block:: ipython

    >> import climetlab_demo_dataset  # Not needed


**Currently**, the best way to know which plugin needs to be installed to access 
a given dataset is to look at :ref:`list of plugins <pluginlist>` (non-exhaustive).

.. todo::

    Design a streamlined way to register and publish plugins.


Xarray for gridded data
-----------------------

Gridded data typically are field data such as temperature or wind
from climate or weather models or satellite images.

    .. code-block:: python

        dsc = climetlab.load_dataset("dataset-name", **options)
        dsc.to_xarray()


Pandas for non-gridded data
---------------------------

None-gridded data typically is tabular non-structured data sucha as observations.
It often includ a column for the latitude and longitude of the data.

    .. code-block:: python

        >>> dsc = climetlab.load_dataset("dataset-name", **options)
        >>> dsc.to_pandas()


Generic options
---------------

Some arguments in the ``options`` dictionary are always included in
``climetlab.load_dataset`` or ``climetlab.Dataset.to_xarray()`` or
``climetlab.Dataset.to_pandas()`` (see :ref:`developer/dataset-options`).

.. todo::
    Currently no options are added by CliMetLab.

Other arguments are defined by the plugin maintainer, and are be
documented in the plugin documentation.

The plugin documentation url is provided by the plugin with :

    .. code-block:: python

        >>> dsc = climetlab.load_dataset("dataset-name")
        >>> dsc = climetlab.dataset("dataset-name")
        >>> dsc.documentation
