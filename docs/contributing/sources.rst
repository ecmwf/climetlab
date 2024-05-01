.. _sources:

How to create a source plugin
=============================

A :doc:`Data source </contributing/sources>` is a Python class that accesses data
from a given location. CliMetLab has build-in sources (the most common being
the "url" source) and a plugin can add more sources capabilities.
A Source provides access to data, the code performing the actual reading can
either be located in the Source itself or delegated to a Reader class.
.. See details in :ref:`Source class </developer/source>`.

.. note::

  **Naming convention**: A plugin package name should preferably starts with ``climetlab-`` and use "-". The Python package to import should starts with
  :py:class:`climetlab\_` and use "_".

Adding a new source as a pip plugin
-----------------------------------

The plugin mechanism for data sources relies on ``entry_points``.
In the ``setup.py`` file of the package, we should have the ``entry_points``
integration as follow:

.. code-block:: python
  :emphasize-lines: 2-4

    setuptools.setup(
        entry_points={"climetlab.sources": [
            "source-name = package_name:ClassName"
            ]
        },
    )

The package name and the class name should match the class defined in the code
of the plugin:

- **source-name**: is the string that will be used in ``cml.load_source("source-name", ...)``
  in oder to trigger the source plugin code.
- **package_name**: is the python package, as it would be used in ``import package_name``
- **ClassName**: is the source class which inherits from ``climetlab.Source``, it must
  be importable from the package_name as ``from package_name import ClassName``.


Example
-------

As an example, the code located at https://github.com/ecmwf/climetlab-demo-source
creates build a pip package named ``climetlab-demo-source``.

This data source plugin allows accessing data from a SQL database using CliMetLab.

Once the plugin is installed (with `pip``), tabular data can be read from as follow:

.. code-block:: python

    >>> import climetlab as cml
    >>> s = cml.load_source(
            "climetlab-demo-source",
            "sqlite:///test.db",
            "select * from data;",
            parse_dates=["time"],
        )
        df = s.to_pandas()

The integration is performed by ``entry_points`` called from ``setup.py``.

.. code-block:: python
  :emphasize-lines: 2-4

    setuptools.setup(
        entry_points={"climetlab.sources": [
            "demo-source = climetlab_demo_source:DemoSource"
            ]
        },
    )
