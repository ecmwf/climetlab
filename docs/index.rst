Welcome to CliMetLab's documentation!
=====================================

.. warning::
   This documentation is work in progress. It is not yet ready.

*CliMetLab* is a Python package aiming at simplifying access to climate and
meteorological datasets, allowing users to focus on science instead of
technical issues such as data access and data formats. It is mostly intended
to be used in Jupyter_ notebooks, and be interoperable with all popular data
analytic packages, such as NumPy_, Pandas_, Xarray_, SciPy_, Matplotlib_, etc.
as well as machine learning frameworks, such as TensorFlow_, Keras_
or PyTorch_. See :ref:`overview` for more information.


.. _Jupyter: https://jupyter.org
.. _NumPy: https://numpy.org
.. _Matplotlib: https://matplotlib.org
.. _Pandas: https://pandas.pydata.org
.. _Xarray: http://xarray.pydata.org
.. _SciPy: https://www.scipy.org
.. _TensorFlow: https://www.tensorflow.org
.. _Keras: https://keras.io
.. _PyTorch: https://pytorch.org


Documentation
-------------


* :doc:`overview`
* :doc:`installing`
* :doc:`firststeps`
* :doc:`examples`

.. toctree::
   :maxdepth: 1
   :hidden:

   overview
   installing
   firststeps
   examples

**User Guide (TODO)**

* :doc:`guide/howtos`
* :doc:`guide/datasets`
* :doc:`guide/sources`
* :doc:`guide/data_handling`
* :doc:`guide/mltools`
* :doc:`guide/plotting`
* :doc:`guide/caching`
* :doc:`guide/settings`
* :doc:`guide/dask`
* :doc:`guide/pluginlist`
* :doc:`guide/cmdline`

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: User Guide

   guide/howtos
   guide/datasets
   guide/sources
   guide/data_handling
   guide/mltools
   guide/plotting
   guide/caching
   guide/settings
   guide/dask
   guide/pluginlist
   guide/cmdline

**Plugin Developer Guide**

* :doc:`contributing/overview`
* :doc:`contributing/datasets`
* :doc:`contributing/datasets_yaml`
* :doc:`contributing/sources`
* :doc:`contributing/normalize`
* :doc:`contributing/availability`
* :doc:`contributing/alias_argument`
* :doc:`contributing/grib`
* :doc:`contributing/plotting`

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Plugin Developer Guide

   contributing/overview
   contributing/datasets
   contributing/datasets_yaml
   contributing/sources
   contributing/normalize
   contributing/availability
   contributing/alias_argument
   contributing/grib
   contributing/plotting


**CliMetLab Developer Guide**

* :doc:`developer/overview`
* :doc:`developer/todolist`
* :doc:`developer/architecture`
* :doc:`developer/plotting`
* :doc:`developer/gallery`
* :doc:`developer/plugins`

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: CliMetLab Developer Guide

   developer/overview
   developer/todolist
   developer/architecture
   developer/plotting
   developer/gallery
   developer/plugins


License
-------

*CliMetLab* is available under the open source `Apache License`__.

__ http://www.apache.org/licenses/LICENSE-2.0.html
