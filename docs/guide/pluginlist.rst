.. _pluginlist:

List of CliMetLab plugins
=========================

.. note::

  This list is **not exhaustive**.
  Some plugins are not listed here because we are not aware of them or because they are for internal
  use only, or not ready to be shared.

  If you would like a plugin to be added in this list, please submit a pull request to CliMetLab
  or `open an issue on github <https://github.com/ecmwf/climetlab/issues>`_.

.. _dataset_plugins:

Dataset plugins
---------------

Installing a :doc:`dataset </guide/datasets>` plugin, allows using an additional dataset
in ``cml.load_dataset``.

- `climetlab-s2s-ai-challenge <https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge>`_:
  Providing data for the Sub-seasonal to Seasonal (S2S)
  Artificial Intelligence Challenge (`https://s2s-ai-challenge.github.io <https://s2s-ai-challenge.github.io/>`_)
  |climetlab-s2s-ai-challenge-build-status|

  Datasets provided: ``s2s-ai-challenge-*``

.. |climetlab-s2s-ai-challenge-build-status| image:: https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge/actions/workflows/check-and-publish.yml/badge.svg
    :alt: build status
    :target: https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge/actions/workflows/check-and-publish.yml


- `climetlab-demo-dataset <https://github.com/ecmwf/climetlab-demo-dataset>`_:
  Demo plugin to illustrate to dataset plugin mechanism.
  |climetlab-demo-build-status|

  Dataset provided: ``demo-dataset``

.. |climetlab-demo-build-status| image:: https://github.com/ecmwf/climetlab-demo-dataset/actions/workflows/python-publish.yml/badge.svg
    :alt: build status
    :target: https://github.com/ecmwf/climetlab-demo-dataset/actions/workflows/python-publish.yml


- `climetlab-tropical-cyclone-dataset <https://github.com/ecmwf-lab/climetlab-tropical-cyclone-dataset>`_:
  Tropical cyclones. In progress.

  Datasets provided: ``tc-*``

- `climetlab-maelstrom-yr <https://github.com/metno/maelstrom-yr>`_:
  Alpha. Gridded weather data for the Nordics, designed for ML postprocessing. Part of the `MAELSTROM <https://www.maelstrom-eurohpc.eu/>`_ project.

  Dataset provided: ``maelstom-yr``

- `climetlab-maelstrom-nogwd <https://git.ecmwf.int/projects/MLFET/repos/maelstrom-nogwd>`_:
  Alpha. Dataset for learning non-orographic gravity wave parametrization. Part of the `MAELSTROM <https://www.maelstrom-eurohpc.eu/>`_ project.

  Dataset provided: ``maelstom-nogwd``

- `climetlab-maelstrom-radiation <https://git.ecmwf.int/projects/MLFET/repos/maelstrom-radiation>`_:
  Alpha. Dataset for learning radiative heating parametrization. Part of the `MAELSTROM <https://www.maelstrom-eurohpc.eu/>`_ project.

  Datasets provided: ``maelstom-radiation``, ``maelstom-radiation-tf``

- `climetlab-maelstrom-ens10 <https://github.com/spcl/climetlab-maelstrom-ens10>`_:
  Alpha. Dataset for testing ensemble postprocessing techniques. Part of the `MAELSTROM <https://www.maelstrom-eurohpc.eu/>`_ project.

  Datasets provided: ``maelstrom-ens5mini``, ``maelstrom-ens10``

- `climetlab-maelstrom-downscaling <https://git.ecmwf.int/projects/MLFET/repos/maelstrom-downscaling-ap5>`_:
  Alpha. Dataset for testing downscaling techniques. Part of the `MAELSTROM <https://www.maelstrom-eurohpc.eu/>`_ project.

  Dataset provided: ``maelstrom-downscaling``

- `climetlab-maelstrom-power-production <https://github.com/4castRenewables/climetlab-plugin-a6>`_:
  Alpha. Dataset for predicting wind farm power production from weather data. Part of the `MAELSTROM <https://www.maelstrom-eurohpc.eu/>`_ project.

  Datasets provided: ``maelstrom-power-production``, ``maelstrom-weather-model-level``, ``maelstrom-weather-pressure-level``, ``maelstrom-weather-surface-level``, ``maelstrom-constants-a-b``

Drafts Dataset Plugins
~~~~~~~~~~~~~~~~~~~~~~
- `climetlab-cems-flood <https://github.com/ecmwf-lab/climetlab-cems-flood>`_:
  Glofas data. In progress.

  Dataset provided: ``glofas``

- `climetlab-eumetnet-postprocessing-benchmark <https://github.com/EUPP-benchmark/climetlab-eumetnet-postprocessing-benchmark>`_:
  |climetlab-eumetnet-postprocessing-benchmark-build-status|

  Eumetnet postprocessing benchmark dataset.

.. |climetlab-eumetnet-postprocessing-benchmark-build-status| image:: https://github.com/EUPP-benchmark/climetlab-eumetnet-postprocessing-benchmark/actions/workflows/check-and-publish.yml/badge.svg
    :alt: build status
    :target: https://github.com/EUPP-benchmark/climetlab-eumetnet-postprocessing-benchmark/actions/workflows/check-and-publish.yml

- `climetlab-meteonet`:
  Meteonet dataset developed by Météo-France.


---


.. _source_plugins:

Source plugins
--------------
Installing a :doc:`source </guide/sources>` plugin, allows using an additional source
in ``cml.load_source``.

- `google-drive <https://github.com/ecmwf-lab/climetlab-google-drive-source>`_
  |climetlab-google-drive-source-build-status|

  Access public files in Google Drive with
  ``cml.load_source("google-drive", file_id="...")``

.. |climetlab-google-drive-source-build-status| image:: https://github.com/ecmwf-lab/climetlab-google-drive-source/actions/workflows/check-and-publish.yml/badge.svg
    :alt: build status
    :target: https://github.com/ecmwf-lab/climetlab-google-drive-source/actions/workflows/check-and-publish.yml


- `climetlab-demo-source <https://github.com/ecmwf/climetlab-demo-source>`_
  |climetlab-demo-source-build-status|

  Demo plugin to illustrate to source plugin mechanism.

.. |climetlab-demo-source-build-status| image:: https://github.com/ecmwf/climetlab-demo-source/actions/workflows/python-publish.yml/badge.svg
    :alt: build status
    :target: https://github.com/ecmwf/climetlab-demo-source/actions/workflows/python-publish.yml


Drafts Source Plugins
~~~~~~~~~~~~~~~~~~~~~

- `stvl <https://github.com/ecmwf-lab/climetlab-stvl>`_
  |climetlab-stvl-build-status|

  Access data the STVL database with
  ``cml.load_source("stvl", ...)``

.. |climetlab-stvl-build-status| image:: https://github.com/ecmwf-lab/climetlab-stvl/actions/workflows/check-and-publish.yml/badge.svg
    :alt: build status
    :target: https://github.com/ecmwf-lab/climetlab-stvl/actions/workflows/check-and-publish.yml
