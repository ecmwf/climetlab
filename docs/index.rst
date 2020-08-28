.. CliMetLab documentation master file, created by
   sphinx-quickstart on Tue Jul 21 11:34:48 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to CliMetLab's documentation!
=====================================

.. warning::
   This documentation is work in progress. It is not yet ready.

**CliMetLab** is a Python package aiming at simplifying access to climate and meteorological datasets, allowing users to focus on science instead of
technical issues such as data access and data formats. It is mostly intended to be used in Jupyter_ notebooks, and be interoperable with all popular
data analytic packages, such as Numpy_, Pandas_, Xarray_, SciPy_, Matplotlib_, etc. and well as machine learning frameworks, such as Tensorflow_, Keras_ or PyTorch_.


.. _Jupyter: https://jupyter.org
.. _Numpy: https://numpy.org
.. _Matplotlib: https://matplotlib.org
.. _Pandas: https://pandas.pydata.org
.. _Xarray: http://xarray.pydata.org
.. _SciPy: https://www.scipy.org
.. _Tensorflow: https://www.tensorflow.org
.. _Keras: https://keras.io
.. _PyTorch: https://pytorch.org


Documentation
-------------

**Getting Started**

* :doc:`overview`
* :doc:`examples`

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Getting Started

   overview
   examples

**User Guide**

* :doc:`guide/howtos`
* :doc:`guide/datasets`
* :doc:`guide/sources`

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: User Guide

   guide/howtos
   guide/datasets
   guide/sources

**Reference**

* :doc:`reference/datasets`
* :doc:`reference/sources`
* :doc:`reference/api`

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Reference

   reference/datasets
   reference/sources
   reference/api


**Contributing**

* :doc:`contributing/datasets`
* :doc:`contributing/sources`

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Contributing

   contributing/datasets
   contributing/sources


License
-------

CliMetLab is available under the open source `Apache License`__.

__ http://www.apache.org/licenses/LICENSE-2.0.html
