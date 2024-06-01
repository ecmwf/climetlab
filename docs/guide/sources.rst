.. _data-sources:

Data sources
============


What is a data Source?
----------------------

A data **Source** is an object created using ``cml.load_source(name, *args, **kwargs)``
with the appropriate name and arguments, which provides access to the data.

A Source also provides metadata and additional functionalities:

- The source **name** is a string that uniquely identifies the source type.

- The **arguments** (args and kwargs) are used to specify the data location to access the data.
  They can include additional parameters to access the data.

- The **additional functionalities** include python code related to caching, plotting and interacting
  with other data.

.. code-block:: python

    >>> import climetlab as cml
    >>> source = cml.load_source(name, *args, **kwargs)

The Source object provides methods to access and use its data such as
``to_xarray()`` or ``to_pandas()`` or ``to_numpy()`` (there are other
:ref:`methods that can be used to access data <base-class-methods>` from a data Source).

.. code-block:: python

    >>> source.to_xarray() # for gridded data
    >>> source.to_pandas() # for non-gridded data
    >>> source.to_numpy() # When the data is a n-dimensional array.
    >>> source.to_tfrecord() # Experimental

.. note::

    :ref:`Source <data-sources>` objects differ from data :ref:`Dataset <datasets>` objects,
    as Datasets refer to a given set of data (such as "the 2m temperature on Europe in 2015",
    while Sources are more generic such as "url").

Which data Sources are available?
---------------------------------

CliMetLab has built-in sources and additional sources can be made available :ref:`as plugins <source_plugins>`.

Built-in data sources:

    - :ref:`data-sources-file` source: Load data from a file.
    - :ref:`data-sources-url` source: Load data from a URL.
    - :ref:`data-sources-url-pattern` source: Load data from list of URL created from a pattern.
    - :ref:`data-sources-cds` source: Load data from the Copernicus Data Store (CDS).
    - :ref:`data-sources-mars` source: Load data from the Meteorological Archival and Retrieval System at ECMWF (MARS).
    - :ref:`data-sources-multi` source: Aggregate multiple sources.
    - :ref:`data-sources-zenodo` source (experimental): Load data from Zenodo.
    - :ref:`data-sources-indexed-urls` source (experimental): Load data from GRIB urls with partial download.



.. _data-sources-file:

file
----

The simplest data source is the ``"file"`` source that accesses a local file.

    .. code:: python

        >>> import climetlab as cml
        >>> data = cml.load_source("file", "path/to/file")
        >>> data.to_xarray() # for gridded data fields
        >>> data.to_pandas() # for non-gridded data

*CliMetLab* will inspect the content of the file to check for any of the
supported data formats listed below:

- Fields:
    - NetCDF
    - GRIB (see :ref:`grib_support`)

- Observations:
    - CSV (comma-separated values)
    - BUFR (https://en.wikipedia.org/wiki/BUFR)
    - ODB (a bespoke binary format for observations)

- Archive formats:
    When given an archive format such as ``.zip``, ``.tar``, ``.tar.gz``, etc,
    *CliMetLab* will attempt to open it and (recursively) extract any usable file.

.. code-block:: python

    >>> import climetlab as cml
    >>> data = cml.load_source("url",
                               "https://www.example.com/data.tgz",
                               unpack=False)
.. todo::

    Support for additionnal formats could be implemented as plugins.

GRIB file example
~~~~~~~~~~~~~~~~~

    .. doctest::

        >>> import climetlab as cml
        >>> data = cml.load_source("file", "examples/test.grib")
        >>> data.to_xarray()
        <xarray.Dataset>
        Dimensions:     (number: 1, time: 1, step: 1, surface: 1, latitude: 11, longitude: 19)
        Coordinates:
          * number      (number) int64 0
          * time        (time) datetime64[ns] 2020-05-13T12:00:00
          * step        (step) timedelta64[ns] 00:00:00
          * surface     (surface) float64 0.0
          * latitude    (latitude) float64 73.0 69.0 65.0 61.0 ... 45.0 41.0 37.0 33.0
          * longitude   (longitude) float64 -27.0 -23.0 -19.0 -15.0 ... 37.0 41.0 45.0
            valid_time  (time, step) datetime64[ns] ...
        Data variables:
            t2m         (number, time, step, surface, latitude, longitude) float32 ...
            msl         (number, time, step, surface, latitude, longitude) float32 ...
        Attributes:
            GRIB_edition:            1
            GRIB_centre:             ecmf
            GRIB_centreDescription:  European Centre for Medium-Range Weather Forecasts
            GRIB_subCentre:          0
            Conventions:             CF-1.7
            institution:             European Centre for Medium-Range Weather Forecasts
            history:                 2022-02-08T10:50 GRIB to CDM+CF via cfgrib-0.9.1...

NetCDF file example
~~~~~~~~~~~~~~~~~~~

    .. doctest::

        >>> import climetlab as cml
        >>> data = cml.load_source("file", "examples/test.nc")
        >>> data.to_xarray()
        <xarray.Dataset>
        Dimensions:     (number: 1, time: 1, step: 1, surface: 1, latitude: 11, longitude: 19)
        Coordinates:
          * number      (number) int64 0
          * time        (time) datetime64[ns] 2020-05-13T12:00:00
          * step        (step) timedelta64[ns] 00:00:00
          * surface     (surface) float64 0.0
          * latitude    (latitude) float64 73.0 69.0 65.0 61.0 ... 45.0 41.0 37.0 33.0
          * longitude   (longitude) float64 -27.0 -23.0 -19.0 -15.0 ... 37.0 41.0 45.0
            valid_time  (time, step) datetime64[ns] ...
        Data variables:
            t2m         (number, time, step, surface, latitude, longitude) float32 ...
            msl         (number, time, step, surface, latitude, longitude) float32 ...
        Attributes:
            GRIB_edition:            1
            GRIB_centre:             ecmf
            GRIB_centreDescription:  European Centre for Medium-Range Weather Forecasts
            GRIB_subCentre:          0
            Conventions:             CF-1.7
            institution:             European Centre for Medium-Range Weather Forecasts
            history:                 2022-02-08T10:50 GRIB to CDM+CF via cfgrib-0.9.1...


Other format file example
~~~~~~~~~~~~~~~~~~~~~~~~~
If the format is supported, see the :ref:`Examples` notebooks for a working example.

If the format is not supported, additional code can be included in CliMetLab to support it.

.. todo::

    Support for additionnal formats could be implemented as plugins.



.. _data-sources-url:

url
---

The ``"url"`` data source is very similar to the ``"file"`` source.

This sources downloads the data from the specified address and stores it in the :ref:`cache <caching>`,
then it operates similarly to the :ref:`"file" source <data-sources-file>` above.
The supported data formats are the same as for the :ref:`"file" source <data-sources-file>`.

.. code-block:: python

    >>> import climetlab as cml
    >>> data = cml.load_source("url", "https://www.example.com/data.csv")

When given an archive format such as ``.zip``, ``.tar``, ``.tar.gz``, etc,
*CliMetLab* will attempt to open it and extract any usable file. If you
want to keep the downloaded file as is, pass ``unpack=False`` to the method.

.. code-block:: python

    >>> import climetlab as cml
    >>> data = cml.load_source("url",
                               "https://www.example.com/data.tgz",
                               unpack=False)


.. _data-sources-url-pattern:

url-pattern
-----------

The ``"url-pattern"`` data source will build urls from the pattern specified,
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
the source ``url`` does (see above the :ref:`data-sources-url` source).


Once the data have been properly downloaded [and unpacked] and cached. It can
can be accessed using ``to_xarray()`` or ``to_pandas()``.

To provide a unique xarray.Dataset (or pandas.DataFrame), the different
datasets are merged.
The default merger strategy for field data is to use ``xarray.open_mfdataset``
from `xarray`. This can be changed by providing a custom merger to the
``url-pattern`` source. See :ref:`merging sources <custom-merge>`



.. _data-sources-cds:

cds
---

The ``"cds"`` data source accesses the `Copernicus Climate Data Store`_ (CDS),
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

The ``"mars"`` source allows handling data from the Meteorological Archival and Retrieval System (MARS).

To figure out which data you need, or discover relevant data available on MARS, see the
publicly accessible `MARS catalog <https://apps.ecmwf.int/archive-catalogue/>`_
(or this `access restricted catalog <https://apps.ecmwf.int/mars-catalogue/>`_).
Notice that various `datasets of interests <https://apps.ecmwf.int/datasets/>`_
are also publicly available.
To access data from the MARS, you will need to register and retrieve an access token.
For a more extensive documentation about MARS, please refer to the
`MARS documentation <https://confluence.ecmwf.int/display/UDOC/MARS+user+documentation>`_ (or its
`access from the internet <https://confluence.ecmwf.int/display/UDOC/Web-MARS>`_ through its
`web API <https://www.ecmwf.int/en/forecasts/access-forecasts/ecmwf-web-api>`_).


.. code-block:: python

    from ecmwfapi import ECMWFDataServer

    server = ECMWFDataServer()

    client.retrieve(
        { "parameter1": "value1",
          "parameter2": "value2",
          ...
        })


to perform the same operation with *CliMetLab*, use the following code:


.. code-block:: python

    import climetlab as cml

    data = cml.load_source("mars",
        { "parameter1": "value1",
          "parameter2": "value2",
          ...
        })


Data downloaded from MARS is stored in the the :ref:`cache <caching>`.

Examples
~~~~~~~~

See the :ref:`Examples` notebooks for a working example.


.. _data-sources-zenodo:

zenodo
------
`Zenodo <https://zenodo.org>`_ is a general-purpose open repository developed and operated by CERN.
It allows researchers to deposit research papers, datasets, etc.
For each submission, a persistent digital object identifier (DOI) is minted,
which makes the stored items easily citeable.

The ``"zenodo"`` source provides access data from `zenodo.org <https://zenodo.org>`_,
including downloading, caching, etc.

.. code:: python

    >>> ds = load_source("zenodo", record_id=...)

Example
~~~~~~~

.. code:: python

    >>> import climetlab as cml
    >>> def only_csv(path):
            return path.endswith(".csv")
    >>> source = cml.load_source("zenodo", record_id=5020468, filter=only_csv)
    >>> source.to_pandas()

.. note::

    Support for zenodo access is experimental.


.. _data-sources-indexed-urls:

indexed_urls
------------

    .. code:: python

        >>> ds = load_source( "indexed-urls", index, request)

Experimental. See :ref:`grib_support`.


.. _data-sources-multi:

multi (advanced usage)
----------------------

    .. code:: python

        >>> ds = load_source( "multi", source1, source2, ...)

.. todo::

    add documentation on multi-source.
