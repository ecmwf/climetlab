.. _caching:

Caching
=======

.. warning::

     This part of CliMetLab is still a work in progress. Documentation and code behaviour will change.



CliMetLab cache configuration is managed through the CliMetLab :doc:`settings`.

The **cache location** is defined by `cache‑directory`.
This cache location does not matter when you are using a unique disk (this is the case for most laptops).
Linux system are different, the default location is assigned by the system for temporary files. If this default location is ``/tmp`` and if ``/tmp`` is mounted separately, it may have size to small for the data you intent to download.
Changing the cache location is detailed in the :doc:`settings` documentation.

.. todo::

    Implement cache invalidation, and checking if there is enough space on disk.

The **cache-minimum-disk-space** option ensures that CliMetLab does not fill your disk.
Its values sets the minimum disk space that must be left on the filesystem.
When the disk space goes below this limit, CliMetLab triggers its cache cleaning mechanism before downloading additional data.
The value of cache-minimum-disk-space can be absolute (such as "10G", "10M", "1K") or relative (such as "10%").

The **cache-maximum-size** option ensures that CliMetLab does not use to much disk space.
Its value sets the maximum disk space used by CliMetLab cache.
When CliMetLab cache disk usage goes above this limit, CliMetLab triggers its cache cleaning mechanism  before downloading additional data.
The value of cache-maximum-size can be absolute (such as "10G", "10M", "1K") or relative (such as "10%").

Notice how the caching options interact:

- Setting `cache-minimum-disk-space=10%` implies `cache-maximum-size=90%`.
- But setting `cache-maximum-size` does not ensure any `cache-minimum-disk-space` because the disk can be filled by data otherwise.

.. warning::

    Setting limits to the cache disk usage ensures that CliMetLab triggers its cache cleaning mechanism before downloading additional data, but it has some limitations.
    As long as the limits are not reached, CliMetLab can add more data into the cache.

    For instance, when downloading a 100G file on your empty disk of 10G total, the download is attempted (since the limits are not reached) and fills the disk and fails with a disk full.



Caching options
---------------

.. module-output:: generate_settings_rst .*-cache-.*


