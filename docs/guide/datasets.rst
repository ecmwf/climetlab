.. _datasets:

Datasets
========

.. todo::

    Explain better what Datasets are.

A :ref:`Dataset <reference/datasets>` is Python class that provide a curated set of data with specific helper functions.

When working on data, we are often writing code to transform, preprocess, adapt the data to our needs.
While it may be very nice to understand deeply to deep magic hunder the hood, this process could very time consuming.
Once somebody did the hard work of massaging the data for a given purpose, their code can be integrated into a dataset plugin and 
made available to others through climetlab. 

Climetlab has build-in datasets (as examples) and most of the datasets are availables as plugins.

Accessing data in a dataset
---------------------------

Once the relevant plugin has been installed, the dataset can be loaded with:

    .. code-block:: python

        climetlab.load_dataset("dataset-name", **options)

The relevant plugin package must be installed to access the dataset, with pip (such as `pip install climetlab-demo-dataset`).
If the package is not installed, climetlab will fail with a NameError exception.

    .. code-block:: python

        climetlab.load_dataset("unknown-dataset")
        NameError: Cannot find dataset 'unknown-dataset' (values are ...),

Note that the plugin name does not have to match the dataset name, as the same plugin may provide several datasets.

.. For example::

    For instance, the plugin `climetlab_sunny_weather` could provide the datasets `sun-flare` and `sun-storm`.
    `pip install climetlab_weather_on_mars` allows to do 
    `climetlab.load_dataset("sun-flare")` and `climetlab.load_dataset("sun-storm")

There is **currently** (this may change) no need to import the plugin package, i.e. no `import climetlab_demo_dataset` to load the dataset `demo-dataset`.
(see how the :ref:`dataset plugins <contributing/dataset>` work to know more).
When sharing a python notebook, it is a good practice to add `!pip install climetlab-...` at the top of the notebook.
It is also possible to add `import climetlab_...` in order to make clear which packages are needed to run the notebook,
especially if the plugin name does not match the dataset name.


Xarray for fields data
----------------------
    .. code-block:: python

        dsc = climetlab.load_dataset("dataset-name", **options)
        dsc.to_xarray()


Pandas for non-gridded data
---------------------------
    .. code-block:: python

        dsc = climetlab.load_dataset("dataset-name", **options)
        dsc.to_pandas()