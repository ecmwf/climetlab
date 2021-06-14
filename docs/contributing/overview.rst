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


The actual integrating your code as a CliMetLab plugin is achieved by creating a package (such as a pip package) or a yaml file.

To make it easier, there is a `template for a Dataset plugin using cookiecutter <https://github.com/ecmwf-lab/climetlab-cookiecutter-dataset>`_.
In addition, for a simple dataset, you can also use a yaml file and rely only on the code provided by CliMetLab or other plugins.

Python documentation on plugins_.

.. _plugins: https://packaging.python.org/guides/creating-and-discovering-plugins/

How else can I to contribute ?
------------------------------
- Submit bug reports, propose enhancements, on github. 
- You can also contribute to the core code by forking and submitting a pull request.
