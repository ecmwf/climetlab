.. _data-handling:

Data Manipulation
=================

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