.. _sources:

Data sources plugins
====================

A :ref:`Data source <data-sources>` is a Python class that accesses data from a
given location. CliMetLab has build-in sources (the most common being the "url"
source) and a plugin can add more sources capabilities.
A Source provides access to data, the code performing the actual reading can either be
located in the Source itself or delegated to a Reader class.
See details in :ref:`Source class <reference/source>`.

Adding a new source as a pip plugin
-----------------------------------

See https://github.com/ecmwf/climetlab-demo-source


    .. code-block:: python
      :emphasize-lines: 2-4

        setuptools.setup(
            entry_points={"climetlab.sources": [
                "demo-source = climetlab_demo_source:DemoSource"
                ]
            },
        )