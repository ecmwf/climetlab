.. _grib_support:

GRIB support
============


.. warning::

    This API is experimental, things may change.

CliMetLab provides built-in functionalities regarging GRIB format handling.
In addition to reading GRIB from local or remote sources, CliMetLab can also
use a precomputed index, avoiding the need to parse the GRIB file to know its
content. Using this index allows partial read of local or remote files, and
merging of mutliple GRIB sources.

CliMetLab can also create GRIB index files through its command line interface.

