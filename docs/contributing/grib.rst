.. _grib_support:

GRIB support
============


CliMetLab provides built-in functionalities regarging GRIB format handling.

Reading GRIB files
------------------

- CliMetLab can read *gridded* GRIB files (or urls) and provide data as ``xarray.Dataset``
  objects. This can be performed using ``cml.load_source("file", "myfile.grib")``.

- In addition to reading GRIB from local or remote sources, CliMetLab can also
  use a precomputed index, avoiding the need to parse the GRIB file to know its
  content. Using this index allows partial read of local files, and
  merging of mutliple GRIB sources.

This can be performed using ``cml.load_source("indexed-directory", "my/dir")``.
To allow fast access to the data in the directory, CliMetLab relies on an index.
Note that the index must have been created on this directory, CliMetLab will create one
(see GRIB indexing below).

Writing GRIB files
------------------

There are two ways to write GRIB files:

- To save data from MARS, CDS or other, when GRIB is already the native format of the data,
use the ``source.save(filename)`` method. This method is implemented only on a sources relying on GRIB.

- CliMetLab also supports writing custom GRIB files, with **modified values or custom attributes**
through the function ```cml.new_grib_output()``. See usage example in the example notebook
(:ref:`examples`).


Building indexes
----------------

CliMetLab can create GRIB index files through its command line interface.


How to build a index for a directory containing GRIB files ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    climetlab index_directory my/dir

This will create a CliMetLab index file in `my/local/dir`,
allowing other to access the data with ``cml.load_source("indexed-directory", "my/dir")``.


How to build a index for **one** given URL containing a GRIB file ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    climetlab index_url "https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/indexed-urls/large_grib_1.grb" > large_grib_1.index

Then upload the file `large_grib_1.index` and make sure it is available at:
"https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/indexed-urls/large_grib_1.index"

This allows accessing the data with

.. code-block:: python

    cml.load_source("indexed-url",
                    "https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/indexed-urls/large_grib_1.grb"
    )


How to build indexes for a set of URLs containing GRIB files ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Or, if you do the same for another URL "https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/indexed-urls/large_grib_2.grb".

.. code-block:: bash

    climetlab index_url "https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/indexed-urls/large_grib_1.grb" > large_grib_1.index
    climetlab index_url "https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/indexed-urls/large_grib_2.grb" > large_grib_2.index

Then upload the files `large_grib_1.index` and `large_grib_2.index` and make sure they are available on the server at:
"https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/indexed-urls/large_grib_1.index"
"https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/indexed-urls/large_grib_2.index"

This allows accessing the data with

.. code-block:: python

    cml.load_source("indexed-urls",
                    "https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/indexed-urls/large_grib_{n}.grb",
                    {"n": [1, 2]},
    )


How to build a index for a set of URLs containing GRIB files ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo::
    Not implemented yet.

.. code-block:: bash

    climetlab index_urls --base-url "https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/indexed-urls" large_grib_1.grb large_grib_2.grb > global_index.index

Then upload the file `global_index.index` and make sure it is available at:
"https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/indexed-urls/global_index.index"

This allows others to access the data with :

.. code-block:: bash
    cml.load_source("indexed-urls",
                    "https://get.ecmwf.int/repository/test-data/climetlab/test-data/input/indexed-urls/global_index.index",
                    {"n": [1, 2]},
    )




How to export files from the CliMetLab cache to another directory ?
-------------------------------------------------------------------

When using CliMetLab to access MARS, CDS or other source, data is cached into the CliMetLab
cache directory (the cache folder is ``climetlab settings cache-directory``).

To prevent the cache from growing forever, old data in the cache directory are deleted automatically
by CliMetLab when new data is downloaded.
CliMetLab can create a shareable directory with some of the data from the cache through its command
line interface.

.. code-block:: bash

    climetlab export_cache DIRECTORY --help


.. todo::
    Update this when mirror implementation changes.
