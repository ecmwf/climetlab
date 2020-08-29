Overview
========

The goal of *CliMetLab* is to simplify access to climate and
meteorological datasets, by hidding the access methods and data formats.

.. code-block:: python

    import climetlab as clm

    data = clm.load_dataset("dataset-name")
    a = data.to_numpy()


The snippet of code above would download the dataset *dataset-name*,
cache it locally and decodes its content in a NumPy array.

.. image:: _static/climetlab.svg
