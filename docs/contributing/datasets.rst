Datasets
========

to do

.. prompt:: yaml \

  ---
  dataset:
    source: url
    args:
      url: http://download.ecmwf.int/test-data/metview/gallery/temp.bufr

    metadata:
      documentation: Sample BUFR file containing TEMP messages


See https://github.com/ecmwf/climetlab-demo-dataset

.. prompt:: python \

  setuptools.setup(
      name="climetlab-demo-dataset",
      version="0.0.1",
      description="Example climetlab external dataset plugin",
      ...
      entry_points={'climetlab.datasets':
              ['demo-dataset = climetlab_demo_dataset']
      },
      ...
  )

ZZ
https://packaging.python.org/guides/creating-and-discovering-plugins/
