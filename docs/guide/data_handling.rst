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

.. _sel:

Selection with `.sel()`
~~~~~~~~~~~~~~~~~~~~~~~

When a CliMetLab data `source` or dataset provides a list of fields, the method ``.sel()`` allows
filtering this list to select a subset of the list of fields.

For instance, the following example shows how to select various subsets of fields for the parameter ``z`` 
from a list of fields:

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

    >>> subset = ds.sel(time=1200)
    >>> len(subset)
    4
    >>> for f in subset:
    GribField(2t,None,20121212,1200,0,0)
    GribField(msl,None,20121212,1200,0,0)
    GribField(2t,None,20121213,1200,0,0)
    GribField(msl,None,20121213,1200,0,0)

    >>> subset = ds.sel(param="2t", time=1200)
    >>> len(subset)
    2
    >>> for f in subset:
    GribField(2t,None,20121212,1200,0,0)
    GribField(2t,None,20121213,1200,0,0)

    >>> subset = ds.sel(param="2t", time=[600, 1200])
    >>> len(subset)
    4
    >>> for f in subset:
    GribField(2t,None,20121212,600,0,0)
    GribField(2t,None,20121212,1200,0,0)
    GribField(2t,None,20121213,600,0,0)
    GribField(2t,None,20121213,1200,0,0)


.. _order_by:

Ordering with `.order_by()`
~~~~~~~~~~~~~~~~~~~~~~~~~~~



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