.. _normalize:

Normalizer
==========

Purpose
-------

When sharing code, a large amount of code is usually
dedicated to processing the arguments of the functions
or methods to check their value and normalize it to a
standard format.

The python language offers the ability to accept a large
range of input type on a unique function through `duck typing`.
This leads to a better integration of the different objects
at stake, for instance to use a ``xarray.Dataset`` as a list
of dates.  TODO: elaborate on this.


CliMetLab offer predefined shortcuts to
implement this. The short API aims to address 80% of
the use cases using the ``@normalize_args`` decorator.
The longer forms aims to tackle specific needs.

Compare the following four codes snippets:


Boilerplate code
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Boilerplate code (extract)
    def __init__(self, date, option):
        if date is None:
          date = DEFAULT_DATE_LIST
        if isinstance(date, tuple):
           date = list(date)
        if not isinstance(date, list):
           date = [date]
        for d in date:
            check_date_is_sunday(d)
        if not option in VALID_OPTIONS:
            raise ValueError(f"option={option} invalid")
        (...)
        (more check and transformations)
        (...)
        do_stuff(date, option)


Using CliMetLab short form API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from climetlab.normalize import normalize_args
    @normalize_args(date="date(%Y%m%d)", option=["foo", "bar"])
    def __init__(self, date, option):
        do_suff(date, option)


Using CliMetLab medium-range API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from climetlab.normalize import normalize_args, Date, Enum
    @normalize_args(date=Date("%Y%m%d", single=False, valid=DEFAULT_DATE_LIST),
    		    option=Enum(["foo", "bar"])
    def __init__(self, date, option):
        do_suff(date, option)


Using CliMetLab fine-control API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo::

    The fine-control API is not implemented.

.. code-block:: python

    from climetlab.normalize import ArgNormalizer, Date, Enum
    norm = ArgNormalizer()
    norm.add_argument("date", Date("%Y%m%d", single=False, valid=DEFAULT_DATE_LIST))
    norm.add_argument("option", Enum(["foo", "bar"])
    norm.available(date=DEFAULT_DATE_LIST, option=["foo", "bar"])
    norm.not_available(date="20211231", option="bar"])
    @norm
    def __init__(self, date, option):
        do_suff(date, option)

The following table lists the available normalizer:

.. list-table::
   :widths: 10 80 10
   :header-rows: 1

   * - Normalizer
     - Trigger
     - Example
   * - :ref:`enum-normalizer`
     - tuple
     - ``option=("a", "b")``
       ``option=Enum("a", "b")``
   * - :ref:`enum-list-normalizer`
     - list
     - ``option=["a", "b"]``
       ``option=EnumList("a", "b")``
   * - :ref:`date-normalizer`
     - "date("
     - ``option="date("%Y%m%d")``
       ``option="Date("%Y%m%d")``
   * - :ref:`date-list-normalizer`
     - "date-list("
     - ``option="date-list("%Y%m%d")``
       ``option="DateList("%Y%m%d")``
   * - :ref:`bounding-box-normalizer`
     - "bounding-box("
     - TODO

.. _enum-normalizer:

Enum
----

The ``Enum`` normalizer pre-process the argument provided when
calling the function, modifies it if needed, and provides a normalised
value to the function. It ensures that the value in the function is an
element of the list provided.


.. code-block:: python

    @normalize_args(option=Enum("a", "b"))
    def f(self, option):
        assert option in ["a", "b"]
        print(option)
    
    >>> f("a")
    "a"
    >>> f(None)
    MissingArgument


Shortcut: An ``Enum`` normalizer is created when a tuple is assigned
to a parameter in @normalize_args.

.. code-block:: python

    @normalize_args(option=("a", "b"))

.. _enum-list-normalizer:

EnumList
--------

The ``EnumList`` normalizer pre-process the argument provided when
calling the function, modifies it if needed, and provides a normalised
value to the function. It ensures the following:

- The value (provided to the function) is a list.
- Each element of this list belong to the list provided.
- If None was provided by the user, the full list is used.

.. code-block:: python

    @normalize_args(option=EnumList("a", "b"))
    def f(self, option):
        for o in option:
            assert o in ["a", "b"]
        print(option)
    
    >>> f("a")
    ["a"]
    >>> f(None)
    ["a", "b"]


Shortcut: An ``Enum`` normalizer is created when a list is assigned
to a parameter in @normalize_args.

.. code-block:: python

    @normalize_args(option=["a", "b"])
    def f(self, option):


.. _date-normalizer:

Date
----

Date and time argument used a lot in Climate and Meteorology code.
The ``Date`` normalizer .

.. code-block:: python

    @normalize_args(date=Date("%Y%m%d"))
    def f(self, date):


Shortcut: An ``Date`` normalizer is created when a string
starting with "date(" is assigned to a parameter in @normalize_args.

.. code-block:: python

    @normalize_args(date="date(%Y%m%d)")


.. _date-list-normalizer:

DateList
--------

The ``DateList`` normalizer is to the ``Date`` normalizer what the ``EnumList`` is to ``Enum``.

.. code-block:: python

    @normalize_args(date=DateList("%Y%m%d"))
    def f(self, date):


Shortcut: An ``DateList`` normalizer is created when a string
starting with "date-list(" is assigned to a parameter in @normalize_args.

.. code-block:: python

    @normalize_args(date="date-list(%Y%m%d)")


.. todo::

    Add more normalizers.
    For instance, for the "parameter" argument such as ```t2m``` or ```tp```.
