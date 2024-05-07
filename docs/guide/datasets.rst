.. _datasets:

Datasets
========

A **Dataset** is an object created using ``cml.load_dataset(name, arg1, arg2=..., ...)``
with the appropriate **name** and **arguments**, which provides access to a clearly well-defined
**dataset**: these data have been defined and curated by somebody providing code along with the data.
It also provides **metadata** and **additional functionalities**.

- The **name** is a string that uniquely identifies the dataset.

- The **argument(s)** ``arg1`` and keyword argument(s) ``arg2`` can be used to specify
  a subset of the dataset.

- The **data** can be accessed using methods such as ``to_xarray()`` or ``to_pandas()``
  or other.

- Relevant **metadata** are attached directly to the dataset to provides
  additional information such as :ref:`an URL, a citation, licence, etc. <dataset metadata>`

- **Additional functionalities**:
  When working on data, we are often writing code to transform, preprocess,
  adapt the data to our needs.
  While it may be very nice to understand deeply to deep magic under the
  hood, this process could be very time-consuming.
  Once somebody else did the hard work of preparing the data for a given
  purpose and designing relevant functions to process it, their code can
  be integrated and made available to others through a CliMetLab dataset
  plugin.
  The Dataset object is an instance of a Python class in which
  the plugin maintainers/users can share additional code.

.. note::

    :ref:`Dataset <datasets>` objects differ from data :ref:`Source <data-sources>` objects,
    as Datasets refer to a given set of data (such as "the 2m temperature on Europe in 2015",
    while Sources are more generic such as "url").


CliMetLab has build-in datasets (as examples) and most of the datasets are
available as plugins (non-exhaustive
:doc:`list of CliMetLab plugins <../guide/pluginlist>`).


.. _accessing_data:

How to load a dataset?
----------------------

The relevant plugin must be installed first, using pip.

    .. code-block:: bash

        pip install climetlab-demo-dataset

This ensures that the dataset can be loaded with
:py:func:`climetlab.load_dataset()`.

    .. code-block:: python

        >>> import climetlab as cml
        >>> ds = cml.load_dataset("demo-dataset")

The first argument is the name of the dataset.
It is used to find the relevant plugin and class to use.
Other arguments are defined by the plugin maintainer and are
documented in the plugin documentation (see :doc:`/guide/pluginlist`).

The Dataset object provides methods to access and use its data such as
``to_xarray()`` or ``to_pandas()`` or ``to_numpy()`` (there are other
:ref:`methods that can be used to access data <base-class-methods>` from a Dataset).

.. code-block:: python

    >>> ds.to_xarray() # for gridded data
    >>> ds.to_pandas() # for non-gridded data
    >>> ds.to_numpy() # When the data is a n-dimensional array.
    >>> ds.to_tfrecord() # Experimental

.. note::

    The name of the python package for a CliMetLab plugin usually starts with "climetlab-".

.. note::

    The plugin name does not necessarily match the dataset name, and one plugin
    can provide several datasets.
    As an example, the plugin ``climetlab-s2s-ai-challenge`` provides
    the datasets ``s2s-ai-challenge-training-input`` and
    ``s2s-ai-challenge-training-output``:

    .. code-block:: ipython

        >>> !pip install climetlab-s2s-ai-challenge
        >>> climetlab.load_dataset("s2s-ai-challenge-training-input", ...)
        >>> climetlab.load_dataset("s2s-ai-challenge-training-output", ...)

Xarray for gridded data
-----------------------

Gridded data typically are field data such as temperature or wind
from climate or weather models or satellite images.

    .. doctest::

        >>> import climetlab as cml
        >>> ds = cml.load_dataset("demo-dataset")
        >>> ds.to_xarray()
        <xarray.Dataset>
        Dimensions:    (latitude: 181, longitude: 360)
        Coordinates:
          * longitude  (longitude) float64 -180.0 -179.0 -178.0 ... 177.0 178.0 179.0
          * latitude   (latitude) float64 90.0 89.0 88.0 87.0 ... -88.0 -89.0 -90.0
        Data variables:
            t2m        (latitude, longitude) float64 273.1 273.3 273.5 ... 250.7 250.6



Pandas for non-gridded data
---------------------------

None-gridded data typically is tabular non-structured data such as
observations.
It often includes a column for the latitude and longitude of the data.

    .. code-block:: python

        >>> import climetlab as cml
        >>> ds = cml.load_dataset("dataset-name", **options)
        >>> ds.to_pandas()


.. _dataset metadata:

Metadata attached to a dataset
------------------------------

Metadata attached to a dataset include the following.

    **home_page**: A link to the home page related to the dataset.

    **licence**: A link to the licence of the dataset.

    **documentation**: A link to the documentation related to the dataset.

    **citation**: A citation related to the dataset.

    **terms_of_use**: A text or link to the terms of use of the data.

    .. doctest::

        >>> import climetlab as cml
        >>> ds = cml.load_dataset("demo-dataset")
        >>> ds.home_page
        'https://github.com/ecmwf/climetlab-demo-dataset'
        >>> ds.documentation
        'Generates a dummy temperature field'


Best practices
--------------
.. note::
    When sharing a python notebook, it is a good practice to add
    ``!pip install climetlab-...`` at the top of the notebook.
    If the package is not installed, CliMetLab fails with a NameError
    exception.


    .. code-block:: python

        >>> # if the package climetlab-demo-dataset is not installed
        >>> import climetlab as cml
        >>> ds = cml.load_dataset("demo-dataset")
        NameError: Cannot find dataset 'demo-dataset' (values are: ...),


    .. code-block:: ipython

        >>> !pip install climetlab_demo_dataset --quiet
        >>> import climetlab as cml
        >>> ds = cml.load_dataset("demo-dataset")
        >>>



There is no need to import the plugin package to enable loading the dataset:

.. code-block:: python

    >>> import climetlab_demo_dataset  # Not needed
