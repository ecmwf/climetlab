.. _data-handling:

Data Manipulation
=================

.. todo::

    This section is a draft.

.. _base-class-methods:

Methods provided by CliMetLab data objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Methods provided by CliMetLab data objects (such as a Dataset, a data Source or a Reader):
Depending on the data, some of these methods are or are not available.

A CliMetLab data object provides methods to access and use its data.

.. code-block:: python

    >>> source.to_xarray() # for gridded data
    >>> source.to_pandas() # for non-gridded data
    >>> source.to_numpy() # When the data is a n-dimensional array.
    >>> source.to_tfrecord() # Experimental

.. todo::

    Explain fields.to_xarray() and obs.to_pandas().

    Explain data[0]

    Add here more details about the .to_... methods.

.. _custom-merge:

Merging Data sources
--------------------

.. warning::

    The merger functionality is experimental, the API may change.

.. todo::

    add documentation on merging. merge=concat(). merge=merge().

.. code-block:: python

    import climetlab as cml
    import xarray as xr

    class MyMerger():
        def __init__(self, *args, **kwargs):
            pass
        def merge(self, paths, **kwargs):
            return xr.open_mfdataset(paths)

    data = cml.load_source("url-pattern",
         "https://www.example.com/data-{foo}-{bar}-{qux}.csv",
         foo = [1,2,3],
         bar = ["a", "b"],
         qux = "unique"
         merger = MyMerger()
         )