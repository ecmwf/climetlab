.. _installing:

Installing
==========

.. warning::
  CliMetLab requires Python 3.6 or above. Depending on your installation
  you may need to substitute ``pip`` to ``pip3`` in the examples below.


Pip install
-----------

To install CliMetLab, simply run the following command:

.. code-block:: bash

  % pip install climetlab

Conda install
-------------

No conda package has been created yet. `pip install climetlab` can be used in a conda environment.

Mixing ``pip`` and ``conda`` could create some dependencies issues, we recommend installing as many dependencies as possible with conda, then install CliMetLab with ``pip``, `as recommended by the anaconda team <https://www.anaconda.com/blog/using-pip-in-a-conda-environment>`_.

.. todo::

  Create a conda package for CliMetLab on conda-forge, with clean dependencies.


Troubleshooting
---------------

No matching distribution found for ...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the installation fails with the following error:

.. code-block:: html

  Collecting ecmwflibs>=x.x.x (from climetlab)
    Could not find a version that satisfies the requirement ecmwflibs>=0.0.90 (from climetlab) (from versions: )
  No matching distribution found for ecmwflibs>=x.x.x (from climetlab)

you will need to make sure that you are using the latest version of ``pip``:

.. code-block:: bash

  % pip install --upgrade pip
  % pip install climetlab

Module enum has no attribute 'IntFlag'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If the installation fails with the following error:

.. code-block:: html

  AttributeError: module 'enum' has no attribute 'IntFlag'

this means that there is an old version of of the ``enum`` package on
your system, that needs to be removed:

.. code-block:: bash

  % pip uninstall -y enum34
  % pip install climetlab
