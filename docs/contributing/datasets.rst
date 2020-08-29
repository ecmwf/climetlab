Datasets
========

to do

.. code-block:: yaml

  ---
  dataset:
    source: url
    args:
      url: http://download.ecmwf.int/test-data/metview/gallery/temp.bufr

    metadata:
      documentation: Sample BUFR file containing TEMP messages


See https://github.com/ecmwf/climetlab-demo-dataset

.. code-block:: python

    setuptools.setup(
        name="climetlab-demo-dataset",
        version="0.0.1",
        description="Example climetlab external dataset plugin",

        entry_points={"climetlab.datasets":
                ["demo-dataset = climetlab_demo_dataset"]
        },

    )



See an `example notebook`_ using an external plugin.

Python documentation on plugins_.

.. _example notebook: ../examples/12-external-plugins.ipynb

.. https://nbsphinx.readthedocs.io/en/0.7.1/a-normal-rst-file.html

.. _plugins: https://packaging.python.org/guides/creating-and-discovering-plugins/
