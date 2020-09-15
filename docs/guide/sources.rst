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

https://www.ecmwf.int/en/forecasts/access-forecasts/ecmwf-web-api

https://www.ecmwf.int/en/forecasts/access-forecasts/ecmwf-web-api

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
