.. _caching:

Caching Settings
================

.. warning::

     This part of CliMetLab is still a work in progress. Documentation
     and code behaviour will change.



CliMetLab cache configuration is managed through the CliMetLab
:doc:`settings`.

The **cache location** is defined by `cache‑directory`.  This cache
location does not matter when you are using a unique disk (this is
the case for most laptops).  Linux system are different, the default
location is assigned by the system for temporary files. If this
default location is ``/tmp`` and if ``/tmp`` is mounted separately,
it may have size to small for the data you intent to download.
Changing the cache location is detailed in the :doc:`settings`
documentation.


The **maximum-cache-size** option ensures that CliMetLab does not
use to much disk space.  Its value sets the maximum disk space used
by CliMetLab cache.  When CliMetLab cache disk usage goes above
this limit, CliMetLab triggers its cache cleaning mechanism  before
downloading additional data.  The value of cache-maximum-size is
absolute (such as "10G", "10M", "1K").

The **maximum-cache-disk-usage** option ensures that CliMetLab
leaves does not fill your disk.  Its values sets the maximum disk
usage space that must be left on the filesystem.  When the disk
space goes below this limit, CliMetLab triggers its cache cleaning
mechanism before downloading additional data.  The value of
maximum-cache-disk-usage is relative (such as "90%" or "100%").

.. warning::
    Notice that the value of `maximum-cache-disk-usage` should not
    be too small.  indeed, your disk may be filled by another
    application, leading to disk usage higher than the value specified
    in your `maximum-cache-disk-usage` setting. In such case,
    CliMetLab will happily delete the data in its cache to make
    room for the other application.

    For instance, setting `maximum-cache-disk-usage` to 80% on a
    1T disk already 70% full, CliMetLab will not cache more than
    100G of data.  When this 80% limit is reached, running an
    external script which writes 100G of data with make it 90%.  On
    the next run, CliMetLab will delete its cache completely.


.. warning::

    Setting limits to the cache disk usage ensures that CliMetLab
    triggers its cache cleaning mechanism before downloading
    additional data, but it has some limitations.  As long as the
    limits are not reached, CliMetLab can add more data into the
    cache.

    For instance, when downloading a 100G file on your empty disk
    of 10G total, the download is attempted (since the limits are
    not reached) and fills the disk and fails with a disk full.



Caching settings
----------------
.. todo::
    
    add pointer to the settings page.

.. module-output:: generate_settings_rst .*-cache-.* cache-.*
