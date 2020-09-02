First steps
===========

Getting data
------------

There are two ways of loading data in *CliMetLab*, using :ref:`datasets <datasets>` or
:ref:`data sources <data-sources>`.

.. code-block:: python

  import climetlab as cml

.. https://www.ncdc.noaa.gov/ibtracs/

.. code-block:: python

    import climetlab as cml

    data = cml.load_source("url",
                          "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/csv/ibtracs.SP.list.v04r00.csv")

    pd = data.to_pandas()
    uma = pd[pd.NAME == "UMA:VELI"]
    cml.plot_map(uma, style="cyclone-track")

.. image:: _static/uma.svg
  :width: 75%

Simple plotting
---------------
*CliMetLab* will try to select the best way to plot data.

.. code-block:: python

    cml.plot_map(data)


Below are the parameters you can pass to the plot function:


.. list-table::
   :header-rows: 1
   :widths: 10 20 10 60

   * - Name
     - Value
     - Default
     - Description

   * - title
     - str or bool
     - ``False``
     - The title of the plot. Use ``True`` for automatic.

   * - projection
     - str
     - ``None``
     - The name of a map projection. Use ``None`` for automatic. See below for possible values.

   * - style
     - str
     - ``None``
     - The name of a plotting to apply. Use ``None`` for default. See below for possible values.

   * - foreground
     - str
     - ``None``
     - TODO. See below for possible values.

   * - background
     - str
     - ``None``
     - TODO. See below for possible values.

   * - path
     - str
     - ``None``
     - Save the plot in a file instead of displaying it.
       The file type is inferred from the path extension (``.png``, ``.pdf``, ``.svg``, ...)

You can find out what are the possible values for *projection*,
*style*, *foreground* and *background* parameters using the code below:

.. code-block:: python

  import climetlab.plotting

  # List of possible projections
  for p in climetlab.plotting.projections():
      print(p)

  # List of possible styles
  for p in climetlab.plotting.styles():
      print(p)

  # List of possible backgrounds/foregrounds
  for p in climetlab.plotting.layers():
      print(p)


To get more information about a given projection, in a Jupyter Notebook:

.. code-block:: python

  from climetlab.plotting import projection

  projection("global")

will output:

.. list-table::
  :header-rows: 0
  :widths: 10 90

  * - Name:
    - global
  * - Collection:
    - projections
  * - Path:
    - /opt/venv/lib/python3.7/site-packages/climetlab/data/projections/global.yaml
  * - Definition:
    - .. code-block:: yaml

        magics:
          mmap:
            subpage_lower_left_latitude: -90.0
            subpage_lower_left_longitude: -180.0
            subpage_map_projection: cylindrical
            subpage_upper_right_latitude: 90.0
            subpage_upper_right_longitude: 180.0

Advanced plotting
-----------------

There are two options to plot several datasets on the same map. If
you do not need to specify data specific parameters (e.g. *style*),
you can call ``cml.plot_map()`` with a list of data objects.

.. code-block:: python

  cml.plot_map((data1, data2), foreground=False)

or, if you want to specify a per-data custom *style*, you can use
``cml.new_map()``:

.. code-block:: python

  p = cml.new_plot(projection="global")
  p.plot_map(data1, style="style1")
  p.plot_map(data2, style="style2")
  p.show()
