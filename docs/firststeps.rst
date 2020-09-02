First steps
===========

Getting data
------------

TODO

Plotting
--------
*CliMetLab* will try to select the best way to plot data.

.. code-block:: python

    cml.plot_map(data)


Below are the parameters you can pass to the plot function:

.. role:: raw-html(raw)
   :format: html

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 50
   :class: climetlab

   * - Name
     - Value
     - Default
     - Description
   * - title
     - str or True
     - ``None``
     - The title of the plot. Use ``True`` for automatic.
   * - projection
     - str
     - ``None``
     - The name of a map projection. Use ``None`` for automatic.
   * - style
     - str
     - ``None``
     - The name of a plotting to apply. Use ``None`` for default.
   * - foreground
     - str
     - ``None``
     - TODO
   * - background
     - str
     - ``None``
     - TODO
   * - path
     - str
     - ``None``
     - Save the plot in a file instead of displaying it.
       The file type is inferred from the path extension (``.png``, ``.pdf``, ``.svg``, ...)
