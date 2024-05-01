.. _plugins-reference:

Climetlab Plugin mechanism
==========================

This document discuss how plugins are integrated into CliMetLab. There are two ways to add
a plugin into CliMetLab:

- A Python package using the standard `Python plugin <https://packaging.python.org/guides/creating-and-discovering-plugins>`_
  mechanism based on ``entry_points``. This is the generic CliMetLab plugin mechanism.

- A YAML file can be also be used to create plugins, when the plugin is simple enough
  and used only generic predefined code.
  (currently only for :doc:`dataset plugins </contributing/datasets>`).

Plugin as python packages using ``entry_points``
------------------------------------------------

During the installation of the pip package, the plugin registers itself thanks to
the entry points in its setup.py file, making CliMetLab aware of the new capabilities.
Then, the user can take advantage of the shared code though the enhanced
:py:func:`climetlab.load_dataset()`, :py:func:`climetlab.load_source()`
and :py:func:`climetlab.plot_map()`, etc.

For ``pip`` packages using ``setuptools``, creating a plugin consists in adding
an entry in ``setup.py``:

.. code-block:: python
  :emphasize-lines: 4-7

    setuptools.setup(
        name = 'climetlab-package-name',
        ...
        entry_points={"climetlab.<plugintype>":
                ["foo = climetlab_package_name:FooClass",
                 "bar = climetlab_package_name:BarClass"]
        },
    )

In this package called **climetlab-package-name**, the class
:py:class:`climetlab_package_name.FooClass` provides Python code related to ``"foo"``.
Additional code related to ``"bar"`` is located in the class
:py:class:`climetlab_package_name.BarClass`.
The **<plugintype>** is one of the plugin type in the table above:
:ref:`dataset <datasets>`,
:ref:`sources <sources>`,
:ref:`readers <readers>`,
etc.
See the individual documentation for each plugin type for detailed examples and
the standard `Python plugin documentation<https://packaging.python.org/guides/creating-and-discovering-plugins>`_.


Plugin as YAML files
--------------------

.. todo::

  This is still a work-in-progress.

Additionally, for :doc:`dataset plugins </contributing/datasets>` only, CliMetLab
search for known locations to find a YAML file with a name matching the requested dataset.
The YAML files are used to create an appropriate class.
