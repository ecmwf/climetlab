.. _plugins-reference:

Climetlab Plugin mechanism
==========================

The generic CliMetLab plugin mechanism relies on creating a python package using
the `python plugin <plugins>`_ mechanism with ``entry_points``. Additionally,
`dataset <datasets>`_ plugins can be created using yaml file.
A Dataset plugin template (https://github.com/ecmwf-lab/climetlab-cookiecutter-dataset)
has been designed to create the boilerplate code for a plugin.

.. note::

  **Naming convention**: the package name should preferably starts with ``climetlab-`` and use "-". The python package to import should starts with
  :py:class:`climetlab\_` and use "_".

After installation, the plugin registers itself thanks to the entry points in the setup.py 
file, making CliMetLab aware of the new capabilities. Then, the user can take advantage of the shared code
though the enhanced :py:func:`climetlab.load_dataset()`, :py:func:`climetlab.load_dataset()`
and :py:func:`climetlab.plot_map()`, etc.

For pip packages using setuptools, creating a plugin consists in adding an entry in ``setup.py``:

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
:py:class:`climetlab_package_name.FooClass` provides python code related to ``"foo"``.
Additional code related to ``"bar"`` is located in the class
:py:class:`climetlab_package_name.BarClass`.
The **<plugintype>** is one of the plugin type in the table above:
:ref:`dataset <datasets>`, 
:ref:`sources <sources>`, 
:ref:`readers <readers>`, 
etc.
See the individual documentation for each plugin type for detailed examples.

.. todo::

  Move from ``setup.py`` to ``setup.cfg`` or ``pytoml``? Add doc for ``conda``?
  Link to documentation about climetlab.plugin.register(). 

.. _plugins: https://packaging.python.org/guides/creating-and-discovering-plugins/

.. automodule:: climetlab.core.plugins
   :members:
   :undoc-members:
   :show-inheritance:
