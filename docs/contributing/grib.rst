.. _grib_support:

GRIB support
============


CliMetLab provides built-in functionalities regarging GRIB format handling.

Reading GRIB files
------------------

CliMetLab can read *gridded* GRIB files and provide data as ``xarray.Dataset``
objects.

Writing GRIB files
------------------

CliMetLab has no support for writing grib files.


GRIB indexing
-------------

.. warning::

    The API regarding the GRIB indexing is experimental, things may change.

In addition to reading GRIB from local or remote sources, CliMetLab can also
use a precomputed index, avoiding the need to parse the GRIB file to know its
content. Using this index allows partial read of local or remote files, and
merging of mutliple GRIB sources.

CliMetLab can also create GRIB index files through its command line interface.

.. todo::

    Add documentation on grib index.

