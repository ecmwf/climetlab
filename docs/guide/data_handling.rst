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

.. _iter:

Iterating
~~~~~~~~~

When a CliMetLab data `source` or dataset provides a list of fields, it can be iterated  over to access each
field (in a given order see :ref:`below <order_by>`).

Let us get a source of fields from the Climate Data Store (CDS) and iterate through the list, each element is a field.

.. code-block:: python

    >>> import climetlab as cml
    >>> ds = cml.load_source(
             "cds",
             "reanalysis-era5-single-levels",
             param=["2t", "msl"],
             product_type="reanalysis",
             grid='5/5',
             date=["2012-12-12", "2012-12-13"],
             time=[600, 1200, 1800],
        )

    >>> len(ds)
    10

    >>> for f in ds: print(f)
    GribField(2t,None,20121212,600,0,0)
    GribField(msl,None,20121212,600,0,0)
    GribField(2t,None,20121212,1200,0,0)
    GribField(msl,None,20121212,1200,0,0)
    GribField(2t,None,20121212,1800,0,0)
    GribField(msl,None,20121212,1800,0,0)
    GribField(2t,None,20121213,600,0,0)
    GribField(msl,None,20121213,600,0,0)
    GribField(2t,None,20121213,1200,0,0)
    GribField(msl,None,20121213,1200,0,0)
    GribField(2t,None,20121213,1800,0,0)
    GribField(msl,None,20121213,1800,0,0)


.. _slice:

Selection with ``[...]``
~~~~~~~~~~~~~~~~~~~~~~~~

When a CliMetLab data `source` or dataset provides a list of fields, it can be :ref:`iterated <iter>` over to access each
field (in a given order see :ref:`below <order_by>`).

A subset of the list can be created using the standard python list interface relying on brackets and slices.

.. code-block:: python

    >>> import climetlab as cml
    >>> ds = cml.load_source(
             "cds",
             "reanalysis-era5-single-levels",
             param=["2t", "msl"],
             product_type="reanalysis",
             grid='5/5',
             date=["2012-12-12", "2012-12-13"],
             time=[600, 1200, 1800],
        )

    >>> len(ds)
    10

    >>> print(f[0])
    GribField(2t,None,20121212,600,0,0)

    >>> for f in ds[0:3]: print(f)
    GribField(2t,None,20121212,600,0,0)
    GribField(msl,None,20121212,600,0,0)
    GribField(2t,None,20121212,1200,0,0)

    >>> for f in ds[0:5:2]: print(f)
    GribField(2t,None,20121212,600,0,0)
    GribField(2t,None,20121212,1200,0,0)
    GribField(2t,None,20121212,1800,0,0)


.. _sel:

Selection with ``.sel()``
~~~~~~~~~~~~~~~~~~~~~~~~~

When a CliMetLab data `source` or dataset provides a list of fields, it can be :ref:`iterated <iter>` over to access each
field (in a given order see :ref:`below <order_by>`).

The method ``.sel()`` allows filtering this list to **select a subset** of the list of fields.

For instance, the following examples shows how to select various subsets of fields from a list of fields.
After selection the required list of fields, the selected data from this subset is available with the
methods ``.to_numpy()``, ``.to_pytorch()``, ``.to_xarray()``, etc...



This list of fields can be filtered to extract on the fields corresponding to the 2m-temperature parameter with ``.sel(param="2t")``:

.. code-block:: python

    >>> import climetlab as cml
    >>> ds = cml.load_source(
             "cds",
             "reanalysis-era5-single-levels",
             param=["2t", "msl"],
             product_type="reanalysis",
             grid='5/5',
             date=["2012-12-12", "2012-12-13"],
             time=[600, 1200, 1800],
        )

    >>> len(ds)
    10

    >>> subset = ds.sel(param="2t")
    >>> len(subset)
    6
    >>> for f in subset:
    GribField(2t,None,20121212,600,0,0)
    GribField(2t,None,20121212,1200,0,0)
    GribField(2t,None,20121212,1800,0,0)
    GribField(2t,None,20121213,600,0,0)
    GribField(2t,None,20121213,1200,0,0)
    GribField(2t,None,20121213,1800,0,0)


This list of fields can be filtered to extract on the fields corresponding to 12h time with ``.sel(time=1200)``:

.. code-block:: python

    >>> import climetlab as cml
    >>> ds = cml.load_source(
             "cds",
             "reanalysis-era5-single-levels",
             param=["2t", "msl"],
             product_type="reanalysis",
             grid='5/5',
             date=["2012-12-12", "2012-12-13"],
             time=[600, 1200, 1800],
        )

    >>> len(ds)
    10
    >>> subset = ds.sel(time=1200)
    >>> len(subset)
    4
    >>> for f in subset:
    GribField(2t,None,20121212,1200,0,0)
    GribField(msl,None,20121212,1200,0,0)
    GribField(2t,None,20121213,1200,0,0)
    GribField(msl,None,20121213,1200,0,0)


Or both filters can be applied simultaneously with ``.sel(param="2t", time=1200)``.

.. code-block:: python

    >>> import climetlab as cml
    >>> ds = cml.load_source(
             "cds",
             "reanalysis-era5-single-levels",
             param=["2t", "msl"],
             product_type="reanalysis",
             grid='5/5',
             date=["2012-12-12", "2012-12-13"],
             time=[600, 1200, 1800],
        )

    >>> len(ds)
    10
    >>> subset = ds.sel(param="2t", time=1200)
    >>> len(subset)
    2
    >>> for f in subset:
    GribField(2t,None,20121212,1200,0,0)
    GribField(2t,None,20121213,1200,0,0)


Filtering on multiple values is also possible by providing a list of values ``.sel(param="2t", time=[600, 1200])``.

.. code-block:: python

    >>> import climetlab as cml
    >>> ds = cml.load_source(
             "cds",
             "reanalysis-era5-single-levels",
             param=["2t", "msl"],
             product_type="reanalysis",
             grid='5/5',
             date=["2012-12-12", "2012-12-13"],
             time=[600, 1200, 1800],
        )

    >>> len(ds)
    10
    >>> subset = ds.sel(param="2t", time=[600, 1200])
    >>> len(subset)
    4
    >>> for f in subset:
    GribField(2t,None,20121212,600,0,0)
    GribField(2t,None,20121212,1200,0,0)
    GribField(2t,None,20121213,600,0,0)
    GribField(2t,None,20121213,1200,0,0)


.. _order_by:

Ordering with ``.order_by()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



.. _custom-merge:

Merging Data sources
====================

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
