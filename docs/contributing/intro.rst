Overview
========

CliMetLab provides a common place to share code used in the Weather and Climate community to do preprocess data, plot it, and include additional tools,
especially for machine leaning purposes. 
In order to avoid rewriting the same code over and over, consider distributing it, the design of CliMetLab allows to do this with plugins.

Target audience
------------------------
This **Contributing** part of the CliMetLab documentation describes how to create plugins (or yaml files) to add data and functionalities to CliMetLab.
The target audience are the plugin maintainers/developers.

If you are using CliMetLab and plugins developed by others, you may prefer reading the **User Guide** of this documentation.

If you are willing to develop further CliMetLab or if you way to achieve something that is not possible with the current plugin framework,
please refer to the **Reference** part of this documentation, which is targeting CliMetLab developers.

How do I share my code ?
------------------------
Depending on what your code does, it can be integrated in CliMetLab differently either as a dataset or a source or a reader or a driver (TODO driver or plotdriver?).


- A new :doc:`dataset <contributing/datasets>`  is the most common case, where you share code to access a curated set data with specific helper functions and you want to help other people to access it with 

    .. code-block:: python

        climetlab.load_dataset("dataset-name", **options)

- A new :doc:`source <contributing/sources>` plugin can be added, when you are sharing code to access a location where there is data. 

    .. code-block:: python

        climetlab.load_source("source-name", **options)

- A new :doc:`reader <contributing/readers>`  plugin is more relevant when you are sharing code to read data on a given format, using specific conventions, or requiring conversions. Readers will be available to the code written for the sources.

- A new :doc:`helper <contributing/plotting>` plugin can be added. This is the plugin you are likely to use when you are sharing code related to plotting data.  Users will use .plot_map() and seamlessly use your code depending on the data they are plotting.

The actual integrating your code as a CliMetLab plugin is achieved by creating a pip package. To make it easier, there is a `template for a Dataset plugin using cookiecutter <https://github.com/ecmwf-lab/climetlab-cookiecutter-dataset>`_.
In addition, for a simple dataset, you can also use yaml file and rely only on the code provided by CliMetLab or other plugins.

How else can I to contribute ?
------------------------------
- Submit bug reports, propose enhancements, on github. 
- You can also contribute to the core code by forking and submitting a pull request.

Python documentation on plugins_.

.. _plugins: https://packaging.python.org/guides/creating-and-discovering-plugins/