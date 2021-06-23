.. _contributing-overview:

Overview
========

*"CliMetLab provides a common place to share code used in the Weather and
Climate community to do preprocess data, plot it, and include additional
tools, especially for machine leaning purposes."*

The is the **contributor guide** part of the CliMetLab documentation, which is
split as follow:

- *Getting started*: General introduction with the main idea described there.
- *User guide*: This is the part you should read if you are using CliMetLab
  and plugins developed by others.
- **Contributor guide**: describes how to create plugins (or yaml files) to add
  data and functionalities to CliMetLab, to make it available to the users
  above. In order to avoid rewriting the same code over and over, consider
  distributing it, the design of CliMetLab allows to do this with plugins.
- *Developers guide*: Please refer to this part either if you are willing to
  develop further CliMetLab or if you want to achieve something that is not
  possible with the current plugin framework.
- *Reference*: The reference documentation of the CliMetLab API and description
  of its internal architecture.

Sharing code
------------
Depending its functionalities, your code can be integrated in CliMetLab
differently either as a dataset or a source or a reader or a helper.


.. _list-plugin-table:

.. list-table::
   :widths: 10 80 10
   :header-rows: 1

   * - Plugin type
     - Use case
     - User API
   * - :doc:`Dataset <datasets>`
     - Sharing code to access a curated set data optionally with additional functionalities.
     - :py:func:`climetlab.load_dataset`
   * - :doc:`Source <sources>`
     - Sharing code to access a new type of location where there is data.
     - :py:func:`climetlab.load_source`
   * - :doc:`Reader <readers>` (DRAFT)
     - Sharing code to read data on a given format, using specific conventions, or requiring conversions. Readers will be available to the code written for the sources.
     - :py:func:`climetlab.load_source`
   * - Helper (DRAFT)
     - Sharing code related to plotting data, enhance data with additional functionalities.
     - :py:func:`climetlab.plot_map`
   * - Machine Learning (TODO)
     - Share weather and climate specific code related to machine learning.
     - :py:class:`climetlab.Dataset` , :py:class:`climetlab.Source`


.. _plugins general:

CliMetLab plugin system
-----------------------

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

How else can I to contribute ?
------------------------------
- Submit bug reports, propose enhancements, on github.
- You can also contribute to the core code by forking and
  submitting a pull request.
