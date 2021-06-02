Introduction
============

Climetlab provides a common place to share code used in the Weather and Climate community to do preprocess data, plot it, and include additional tools,
especially for machine leaning purposes. 
In order to avoid rewriting the same code over and over, consider distributing it, the design of Climetlab allows to do this with plugins.

How do I share my code ?
------------------------
Depending on what you code does, it can be integrated in climetlab differently either as a dataset or a source or a reader or a driver (TODO driver or plotdriver?).


- A new :doc:`dataset <contributing/datasets>`  is the most common case, where you share code to access a curated set data with specific helper functions and you want to help other people to access it with 


    .. code-block:: python
      :emphasize-lines: 2-4

        climetlab.load_dataset("dataset-name", **options)

- A new :doc:`source <contributing/sources>` plugin can be added, when you are sharing code to access a location where there is data. 

    .. code-block:: python
      :emphasize-lines: 2-4

        climetlab.load_source("source-name", **options)

- A new :doc:`reader <contributing/readers>`  plugin is more relevant when you are sharing code to read data on a given format, using specific conventions, or requiring conversions. Readers will be available to the code written for the sources.

- A new :doc:`plotting driver <contributing/plotdriver>` (TODO graphicdriver?) plugin can be added, when you are sharing code plotting data. Users will use .plot_map() and seamlessly use your code.

The actual integrating your code as a Climetlab plugin is achieved by creating a pip package. To make it easier, there is a `template for a Dataset plugin using cookiecutter <https://github.com/ecmwf-lab/climetlab-cookiecutter-dataset>`_.
Additionaly, for a simple dataset, you can also use yaml file and rely only on the code provided by climetlab or other plugins.

How else can I to contribute ?
------------------------------
- Submit bug reports, propose enhancements, on github. 
- You can also contribute to the core code by forking and submitting a pull request.