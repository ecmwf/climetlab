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
   :widths: 10 20 10 60
   :class: climetlab

   * - Name
     - Value
     - Default
     - Description
   * - title
     - str or ``True``
     - ``None``
     - The title of the plot. Use ``True`` for automatic.
   * - projection
     - str
     - ``None``
     - The name of a map projection. Use ``None`` for automatic. To find out about
       the list of available projections:
          .. code-block:: python

             from climetlab.plotting import projections

             for p in projections():
                 print(p)

   * - style
     - str
     - ``None``
     - The name of a plotting to apply. Use ``None`` for default. To find out about
       the list of available projections
          .. code-block:: python

             from climetlab.plotting import styles

             for p in styles():
                 print(p)
   * - foreground
     - str
     - ``None``
     - TODO. To find out about
       the list of available foregrounds
          .. code-block:: python

             from climetlab.plotting import layers

             for p in layers():
                 print(p)
   * - background
     - str
     - ``None``
     - TODO. To find out about
       the list of available backgrounds
          .. code-block:: python

             from climetlab.plotting import layers

             for p in layers():
                 print(p)
   * - path
     - str
     - ``None``
     - Save the plot in a file instead of displaying it.
       The file type is inferred from the path extension (``.png``, ``.pdf``, ``.svg``, ...)
