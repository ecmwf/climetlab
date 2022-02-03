Settings
========


*CliMetLab* is maintaining a set of global settings which control
its behaviour.

The settings are saved in ``~/.climetlab/settings.yaml``. They can
be accessed from Python or using the ``climetlab`` command line as shown below:

.. todo::

    Add documentation for command line usage.

Accessing settings
------------------

.. literalinclude:: settings-1-get.py

Changing settings
-----------------

.. literalinclude:: settings-2-set.py

Resetting settings
------------------

.. literalinclude:: settings-3-reset.py

.. note::

    It is recommended to restart your Jupyter kernels after changing
    or resetting settings.

Default values
--------------

.. module-output:: generate_settings_rst
