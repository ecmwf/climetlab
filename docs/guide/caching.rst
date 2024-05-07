.. _caching:

Caching
=======

.. warning::

     This part of CliMetLab is still a work in progress. Documentation
     and code behaviour will change.


Purpose
-------

CliMetLab caches most of the remote data access on a local cache. Running again
``cml.load_dataset`` or ``cml.load_source`` will use the cached data instead of
downloading it again.
When the cache is full, cached data is deleted according it cache policy
(i.e. oldest data is deleted first).
CliMetLab cache configuration is managed through the CliMetLab :doc:`settings`.

.. warning::

    The CliMetLab cache is intended to be used by a single user.
    Sharing cache with **multiple users is not recommended**.
    Downloading a local copy of data on a shared disk to have multiple
    users working is a different use case and should be supported
    through using mirrors.
    `Feedback and feature requests are welcome. <https://github.com/ecmwf/climetlab/issues>`_

.. _cache_location:

Cache location
--------------

  The cache location is defined by the ``cache‑directory`` setting. Its default
  value depends on your system:
    - ``/tmp/climetlab-$USER`` for Linux,
    - ``C:\\Users\\$USER\\AppData\\Local\\Temp\\climetlab-$USER`` for Windows
    - ``/tmp/.../climetlab-$USER`` for MacOS


  The cache location can be read and modified either with shell command or within python.

  .. note::

    It is recommended to restart your Jupyter kernels after changing
    the cache location.

  From a shell with the ``climetlab`` command:

  .. code:: bash

    # Find the current cache directory
    $ climetlab settings cache-directory
    /tmp/climetlab-$USER

    # Change the value of the setting
    $ climetlab settings cache-directory /big-disk/climetlab-cache

    # Cache directory has been modified
    $ climetlab settings cache-directory
    /big-disk/climetlab-cache

  From a python notebook or python script:

  .. code:: python

    >>> import climetlab as cml
    >>> cml.settings.get("cache-directory") # Find the current cache directory
    /tmp/climetlab-$USER
    >>> # Change the value of the setting
    >>> cml.settings.set("cache-directory", "/big-disk/climetlab-cache")

    # Python kernel restarted

    >>> import climetlab as cml
    >>> cml.settings.get("cache-directory") # Cache directory has been modified
    /big-disk/climetlab-cache

  More generally, the CliMetLab settings can be read, modified, reset
  to their default values using the ``climetlab`` command or from python,
  see the :doc:`Settings documentation <settings>`.

Cache limits
------------

Maximum-cache-size
  The ``maximum-cache-size`` setting ensures that CliMetLab does not
  use to much disk space.  Its value sets the maximum disk space used
  by CliMetLab cache.  When CliMetLab cache disk usage goes above
  this limit, CliMetLab triggers its cache cleaning mechanism  before
  downloading additional data.  The value of cache-maximum-size is
  absolute (such as "10G", "10M", "1K").

Maximum-cache-disk-usage
  The ``maximum-cache-disk-usage`` setting ensures that CliMetLab
  leaves does not fill your disk.
  Its values sets the maximum disk usage of the filesystem containing the cache
  directory. When the disk space goes below this limit, CliMetLab triggers
  its cache cleaning mechanism before downloading additional data.
  The value of maximum-cache-disk-usage is relative (such as "90%" or "100%").

.. warning::
    If your disk is filled by another application, CliMetLab will happily
    delete its cached data to make room for the other application as soon
    as it has a chance.

.. note::
    When tweaking the cache settings, it is recommended to set the
    ``maximum-cache-size`` to a value below the user disk quota (if appliable)
    and ``maximum-cache-disk-usage`` to ``None``.


Caching settings default values
-------------------------------

.. module-output:: generate_settings_rst .*-cache-.* cache-.*

Other CliMetLab settings can be found :ref:`here <settings_table>`.
