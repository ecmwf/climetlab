.. _contributing-overview:

Overview
========

  *"CliMetLab provides a common place to share code used in the Weather and
  Climate community to preprocess data, plot it, and include additional
  tools, especially for machine learning purposes."*

.. warning::

  CliMetLab is still a work in progress: Backward compatibility is not ensured
  as long a version 1.0 is not released (see :ref:`todo list <todolist>`).
  Nevertheless, the API and functionalities provided for the dataset and source
  plugins are **mostly** stable and already usable.

The **plugins developer guide** part of the CliMetLab documentation
describes how to create plugins (or YAML files) to add
data and functionalities to CliMetLab, to make it available to the end-users.

Sharing code using plugins
--------------------------

In order to avoid rewriting the same code over and over, consider
distributing it, the design of CliMetLab allows this through plugins
developed by data providers and data users and other stakeholders.

CliMetLab has several types of plugins.

   - :doc:`Dataset plugin<datasets>`
   - :doc:`Sources plugin<sources>`
   - :doc:`Reader plugin<readers>` (draft)
   - Helper plugin (draft)
   - Machine learning plugin (not yet implemented)


Depending on the functionalities provided by your code, it can be integrated
in CliMetLab differently either as a dataset or a source or a reader or a
helper plugin (please refer to the table below.)
If you are distributing or referring to a dataset, the right plugin type
for you is likely to be a :doc:`dataset plugin <datasets>`.

For more details, here is also a general description of the
:ref:`CliMetLab plugin mechanism <plugins-reference>`.


.. _list-plugin-table:

.. list-table::
   :widths: 10 80 10
   :header-rows: 1

   * - Plugin type
     - Use case
     - End-User API
   * - :doc:`Dataset <datasets>`
     - Sharing code to access a curated dataset optionally with additional functionalities.
     - :py:func:`climetlab.load_dataset`
   * - :doc:`Source <sources>`
     - Sharing code to access a new type of location where there are data.
     - :py:func:`climetlab.load_source`
   * - :doc:`Reader <readers>` (DRAFT)
     - Sharing code to read data on a given format, using specific conventions, or requiring conversions. Readers will be available to the code written for the sources.
     - :py:func:`climetlab.load_source`
   * - Helper (DRAFT)
     - Sharing code related to plotting data, enhancing data with additional functionalities.
     - :py:func:`climetlab.plot_map`
   * - Machine Learning (TODO)
     - Sharing weather and climate specific code related to machine learning.
     - :py:class:`climetlab.Dataset` , :py:class:`climetlab.Source`



How else can I contribute?
------------------------------

See the :ref:`todo list <todolist>`.
