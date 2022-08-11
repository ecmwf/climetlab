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

This can be performed using ``cml.load_source("directory", "my/directory")``.
To allow fast access to the data in the directory, CliMetLab relies on an index.
If the index has not been created already, CliMetLab will create one
(see GRIB indexing below).

Writing GRIB files
------------------

CliMetLab has no support for writing grib files.


How to build a index for a directory containing GRIB files ?
------------------------------------------------------------

CliMetLab can create GRIB index files through its command line interface.


.. code-block:: bash

    climetlab index_directory DIRECTORY --help


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