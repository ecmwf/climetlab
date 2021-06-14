.. _datasets:

Datasets
========

A ``Dataset`` is a Python class providing a curated set of data with specific helper functions.

When working on data, we are often writing code to transform, preprocess, adapt the data to our needs.
While it may be very nice to understand deeply to deep magic under the hood, this process could very time consuming.
Once somebody else did the hard work of preparing the data for a given purpose and designing relevant functions to process it,
their code can be integrated into a dataset plugin and made available to others through a CliMetLab plugin. 

CliMetLab has build-in datasets (as examples) and most of the datasets are available as plugins.

Accessing data in a dataset
---------------------------

Once the relevant plugin has been installed, the dataset can be loaded with :py:func:`load_dataset()` as follows:


    .. code-block:: python

        !pip install --quiet climetlab-demo-dataset
        import climetlab as cml

        ds = cml.load_dataset("demo-dataset")

The relevant plugin package **must be installed** to access the dataset, with pip (such as ``pip install climetlab-demo-dataset``).
If the package is not installed, CliMetLab will fail with a NameError exception.

    .. code-block:: python

        ds = climetlab.load_dataset("demo-dataset")
        NameError: Cannot find dataset 'demo-dataset' (values are ...),

When sharing a python notebook, it is a good practice to add
`!pip install climetlab-...` at the top of the notebook.
There is **currently** (this may change) no need to import the plugin package,
i.e. no `import climetlab_demo_dataset` to load the dataset `demo-dataset`.
(see how the :ref:`dataset plugins <contributing/datasets>` work to know more).
It is also possible to add  `import climetlab_...` in order to make clear
which packages are needed to run the notebook, especially if the plugin
name does not match the dataset name.

Note that the plugin name does not have to match the dataset name, and the same plugin may provide several datasets.

.. For example::

    For instance, the plugin `climetlab_weather_on_sun` could provide the datasets `sun-flare` and `sun-storm`.
    `pip install climetlab_weather_on_sun` allows to do 
    `climetlab.load_dataset("sun-flare")` and `climetlab.load_dataset("sun-storm")
Xarray for gridded data
-----------------------

Gridded data typically are field data such as temperature or wind from climate or weather models or satellite images.

    .. code-block:: python

        dsc = climetlab.load_dataset("dataset-name", **options)
        dsc.to_xarray()


Pandas for non-gridded data
---------------------------

None-gridded data typically is tabular non-structured data sucha as observations.
It often includ a column for the latitude and longitude of the data.

    .. code-block:: python

        dsc = climetlab.load_dataset("dataset-name", **options)
        dsc.to_pandas()


Additionnal options
-------------------

Some arguments in the ``options`` dictionary are always included in ``climetlab.load_dataset`` or ``climetlab.Dataset.to_xarray()``  or ``climetlab.Dataset.to_pandas()`` (see :ref:`developer/dataset-options`).

.. todo::
    Currently no options are added by CliMetLab.

Other arguments are defined by the plugin maintainer, and should be documented in the plugin documentation.

The plugin documentation url is provided by the plugin with :

    .. code-block:: python

        dsc = climetlab.load_dataset("dataset-name")
        # dsc = climetlab.dataset("dataset-name")
        # dsc = climetlab.Dataset("dataset-name")
        # dsc = climetlab.info_dataset("dataset-name")
        dsc.documentation

.. todo::
    Choose one solution above and implement it.
    