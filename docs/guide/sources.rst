.. _data-sources:

Data sources
============

.. todo::

    Explain what are Data sources. List the built-in ones.
    Explain fields.to_xarray() and obs.to_pandas().
    Explain data[0]


.. code-block:: python

    import climetlab as cml

    data = cml.load_source("source-name",
                           "parameter1",
                           "parameter2", ...)

.. _data-sources-file:

file
----

The simplest data source is the *file* source that accesses a local file.


.. code-block:: python

    import climetlab as cml

    data = cml.load_source("file", "/path/to/file")


*CliMetLab* will inspect the content of the file to check for any of the
supported data formats listed below:

- Fields:
    - NetCDF
    - GRIB

- Observations:
    - CSV
    - BUFR
    - ODB (a bespoke binary format for observations)



.. _data-sources-url:

url
---

The *url* data source will download the data from the address
specified and store it in the :ref:`cache <caching>`. The supported
data formats are the same as for the *file* data source above.

.. code-block:: python

    import climetlab as cml

    data = cml.load_source("url", "https://www.example.com/data.csv")



When given an archive format such as ``.zip``, ``.tar``, ``.tar.gz``, etc,
*CliMetLab* will attempt to open it and extract any usable file. If you
want to keep the downloaded file as is, pass ``unpack=False`` to the method.

.. code-block:: python

    import climetlab as cml

    data = cml.load_source("url",
                           "https://www.example.com/data.tgz",
                           unpack=False)


.. _data-sources-url-pattern:

url-pattern
-----------

The *url-pattern* data source will build urls from the pattern specified,
using the other arguments to fill the pattern. Each argument can be a list
to iterate and create the cartesian product of all lists.
Then each url is downloaded and stored it in the :ref:`cache <caching>`. The
supported download the data from the address data formats are the same as
for the *file* and *url* data sources above.

.. code-block:: python

    import climetlab as cml

    data = cml.load_source("url-pattern",
         "https://www.example.com/data-{foo}-{bar}-{qux}.csv",
         foo = [1,2,3],
         bar = ["a", "b"],
         qux = "unique"
         )

The code above will download and process the data from the six following urls:

#. \https://www.example.com/data-1-a-unique.csv
#. \https://www.example.com/data-2-a-unique.csv
#. \https://www.example.com/data-3-a-unique.csv
#. \https://www.example.com/data-1-b-unique.csv
#. \https://www.example.com/data-2-b-unique.csv
#. \https://www.example.com/data-3-b-unique.csv

If the urls are pointing to archive format, the data will be unpacked by
``url-pattern`` according to the **unpack** argument, similarly to what
the source ``url`` does (see above :ref:`data-sources-url`)



.. todo:

    test `to_pandas()` with `url-pattern`.

Once the data have been properly downloaded [and unpacked] and cached. It can
can be accessed using ``to_xarray()`` or ``to_pandas()``.

To provide a unique xarray.Dataset (or pandas.DataFrame), the different
datasets are merged.
The default merger strategy for field data is to use ``xarray.open_mfdataset``
from `xarray`. This can be changed by providing a merger to the
``url-pattern`` source:

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


.. warning::

    The merger functionality is experimental, the API may change.

.. _data-sources-cds:

cds
---

This data source access the `Copernicus Climate Data Store`_ (CDS),
using the cdsapi_ package.  A typical *cdsapi* request has the
following format:



.. code-block:: python

    import cdsapi

    client = cdsapi.Client()

    client.retrieve("dataset-name",
                    {"parameter1": "value1",
                     "parameter2": "value2",
                     ...})


to perform the same operation with *CliMetLab*, use the following code:


.. code-block:: python

    import climetlab as cml

    data = cml.load_source("cds",
                           "dataset-name",
                           {"parameter1": "value1",
                            "parameter2": "value2",
                            ...})


Data downloaded from the CDS is stored in the the :ref:`cache <caching>`.

To access data from the CDS, you will need to register and retrieve an
access token. The process is described here_.

For more information, see the CDS `knowledge base`_.

.. _Copernicus Climate Data Store: https://cds.climate.copernicus.eu/

.. _here: https://cds.climate.copernicus.eu/api-how-to
.. _cdsapi: https://pypi.org/project/cdsapi/
.. _knowledge base: https://confluence.ecmwf.int/display/CKB/Copernicus+Knowledge+Base

.. _data-sources-mars:



mars
----

Meteorological Archival and Retrieval System (MARS)

.. _public datasets: https://apps.ecmwf.int/datasets/

.. _catalogue: https://www.ecmwf.int/en/forecasts/datasets/archive-datasets

.. _WebMARS: https://confluence.ecmwf.int/display/UDOC/Web-MARS
.. _documentation: https://confluence.ecmwf.int/display/UDOC/MARS+user+documentation


.. _webapi: https://www.ecmwf.int/en/forecasts/access-forecasts/ecmwf-web-api

.. code-block:: python

    from ecmwfapi import ECMWFDataServer

    server = ECMWFDataServer()

    client.retrieve({
        "parameter1": "value1",
        "parameter2": "value2",
    ...})


to perform the same operation with *CliMetLab*, use the following code:


.. code-block:: python

    import climetlab as cml

    data = cml.load_source("mars",
                           {"parameter1": "value1",
                            "parameter2": "value2",
                            ...})



Data downloaded from MARS is stored in the the :ref:`cache <caching>`.

multi
-----

TODO
