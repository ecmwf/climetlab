Installing
==========

.. warning::
  CliMetLab requires Python 3.6 or above. Depending on your installation
  you may need to substitute ``pip`` to ``pip3`` in the examples below.


To install climetlab, simply run the following command:

.. code-block:: bash

  % pip install climetlab

If the installation fails with the following error:

.. code-block::

  Collecting ecmwflibs>=x.x.x (from climetlab)
    Could not find a version that satisfies the requirement ecmwflibs>=0.0.90 (from climetlab) (from versions: )
  No matching distribution found for ecmwflibs>=x.x.x (from climetlab)

you will need to make sure that you are using the latest version of ``pip``:

.. code-block:: bash

  % pip install --upgrade pip
  % pip install climetlab

If the installation fails with the following error:

.. code-block::

  AttributeError: module 'enum' has no attribute 'IntFlag'

this means that there is an old version of of the ``enum`` package on
your system, that needs to be removed:

.. code-block:: bash

  % pip uninstall -y enum34
  % pip install climetlab
