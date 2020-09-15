.. _data-sources:

Data sources
============

.. todo::

    Explain what are Data sources. List the built-in ones.


.. _data-sources-file:

file
----

.. code-block:: python

    import climetlab as cml

    data = cml.load_source("file", "/path/to/file")


Supported data types are:

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

https://www.ecmwf.int/en/forecasts/datasets/archive-datasets
https://apps.ecmwf.int/datasets/
https://confluence.ecmwf.int/display/UDOC/Web-MARS
https://confluence.ecmwf.int/display/UDOC/MARS+user+documentation


multi
-----
