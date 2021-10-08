Climetlab CLI
=============

Installing climetlab also make available the :code:`climetlab` utility command line interface.

Usage
-----

.. code:: bash

    $ climetlab <command> [options]

.. code:: bash

    $ climetlab
    (climetlab) <command> [options]

Interactive prompt
------------------
:code:`climetlab`

Running the :code:`climetlab` command with no argument starts the interactive prompt. Autocompletion is enabled on the interactive prompt.

    .. code:: bash

        $ climetlab
        (climetlab) <command> [options]
        (climetlab) 

cache
-----
:code:`climetlab cache [options]`

Provides information about the CliMetLab cache

Running the :code:`climetlab cache` command with no argument list the whole cache content.

Example:

    .. code:: bash

        $ climetlab
        (climetlab) cache --full

decache
-------
:code:`climetlab decache options`

Perform full or partial decaching, i.e. clean, i.e. delete files in the CliMetLab cache. Running the :code:`climetlab decache` command requires some arguments.

* --all: TODO

* --newer: TODO

* --older: TODO

* --smaller: TODO

* --larger: TODO

Example:

    .. code:: bash

        $ climetlab
        (climetlab) <command> [options]
        (climetlab) 

Help
----
:code:`climetlab help`

Provide a list of available commands.