Settings
========

*CliMetLab* is maintaining a set of global settings which control
its behaviour.

The settings are saved in ``~/.climetlab/settings.yaml``. They can
be accessed from Python or using the ``climetlab`` command line.

Accessing settings
------------------

CliMetLab settings can be accessed using the python API:

.. literalinclude:: settings-1-get.py

Or through the command line interface.

.. code:: bash

    $ climetlab settings cache-directory

Or using the ``climetlab`` interactive prompt:

.. code:: bash

    $ climetlab
    (climetlab) settings cache-directory


Changing settings
-----------------

.. note::

    It is recommended to restart your Jupyter kernels after changing
    or resetting settings.

CliMetLab settings can be modified using the python API:

.. literalinclude:: settings-2-set.py

Or through the command line interface (CLI). Note that changing settings containing
dictionary values is not possible with the CLI.

.. code:: bash

    $ climetlab settings cache-directory /big-disk/climetlab-cache

Or using the ``climetlab`` interactive prompt:

.. code:: bash

    $ climetlab
    (climetlab) settings cache-directory /big-disk/climetlab-cache



Resetting settings
------------------

.. note::

    It is recommended to restart your Jupyter kernels after changing
    or resetting settings.

CliMetLab settings can be reset using the python API:

.. literalinclude:: settings-3-reset.py

Or through the command line interface (CLI):

.. code:: bash

    $ climetlab settings_reset cache-directory
    $ climetlab settings_reset --all

Or using the ``climetlab`` interactive prompt:

.. code:: bash

    $ climetlab
    (climetlab) settings_reset
    To wipe the cache completely, please use the --all flag. Use --help for more information.
    (climetlab) settings_reset --all
    (climetlab) Ctrl^D


.. _settings_table:

Default values
--------------

.. module-output:: generate_settings_rst
