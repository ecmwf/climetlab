.. _normalize:

Normalize (decorator)
=====================

This section discuss the purpose of the `@normalize` decorator,
show how to use it and provides reference documentation.

Purpose
-------

When sharing code, a large amount of code is usually
dedicated to processing the arguments of the functions
or methods to check their value and normalize it to a
standard format.

The python language offers the ability to accept a large
range of input type on a unique function through `duck typing`.
This leads to a better integration of the different objects
at stake, for instance using an object such as ``xarray.Dataset``
or a ``pandas.DataFrame`` or ``pandas.Serie`` as input
to provide a list of dates.


CliMetLab offers predefined shortcuts to
implement this. The short API aims to address 80% of
the use cases using the ``@normalize`` decorator.
The longer forms aims to tackle specific needs.

Compare the following codes snippets:


.. dropdown:: Boilerplate code
    :open:

    Tedious and error-prone python code is needed to check
    and normalize the values of the function arguments given
    by the user.
    
    .. code-block:: python
    
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


.. dropdown:: Using CliMetLab short form API
    :open:

    The decorator `@normalize_args` provides generic default behaviour
    to handle domain specific arguments (for dates, meteorological and climate
    parameters, bounding boxes, etc.)

    .. code-block:: python

        from climetlab.normalize import normalize_args
        @normalize_args(date="date(%Y%m%d)", option=["foo", "bar"])
        def __init__(self, date, option):
            do_suff(date, option)


.. _howto-normalizer:

How to use
----------

- How to ensure that the value in the function belong to a list ?

    .. code-block:: python

        from climetlab.decorator import normalize

        @normalize(param, ["tp", "gh"])
        def f(self, param):
            print(param)


- How to ensure that the value in the function is a date
  with format "YYYY-MM-DD"?

    .. code-block:: python

        from climetlab.decorator import normalize

        @normalize(option, "date(%Y-%m-%d)""
        def f(self, option):
            print(option)

- How to ensure that the value in the function is a list?
    Add the keyword argument `multiple=True`. Not available for ``bounding-box``.
  
- How to ensure that the value in the function is not a list?
    Add the keyword argument `multiple=False`.

- How to accept list or non-list as input?
    Add the keyword argument `multiple=None`. Not available for ``bounding-box``.


- How to add alias/shortcuts/special values to be replaced by actual predefined values?
    Use the keyword argument `alias` and provide a dictionary.

    .. code-block:: python

        from climetlab.decorator import normalize

        @normalize( "x", aliases={"one": 1})
        def f(x):
            return x
        
    .. code-block:: python

        from climetlab.decorator import normalize

        DATES = dict(
            april=["20210401", "20210402", "20210403"],
            june=["20210610", "20210611"],
        )
        @normalize( "x", "date-list(YYYYMMDD)", aliases=DATES)
        def f(x):
            return x


Reference
---------

.. todo::

    This API is experimental, things may change.


``@normalize(name, values, aliases={}, multiple=None, **kwargs)``

The ``@normalize`` decorator the arguments provided when calling the
the decorated function, modifies it if needed, and provides a normalised
value to the function. It ensures that the value in the function is what
is expected to be processed by the function.


values
    If `values` is a list, the list of allowed values for the parameter.
    If `values` is a string, it is expected to be a shortcut similar to
    "type(options)" where `type` is one of the following: 'date', 'date-list',
    'bounding-box'.
    These shorts cut aims at providing a easy way to define many options in
    a more concise manner.
    Example: "date-list(%Y%m%d)"

type
    Type of value expected by the function. The type should be one of the
    following: 'str', 'int', 'float', 'date', 'date-list', 'str-list',
    'int-list', 'float-list'.


format
    The keyword argument `format`
    is available for `type`
    ='date' and
    'date-list'.
    It provides the expected format according to `datetime.strftime`.
    Example: format='%Y%m%d'

convention
    Experimental. To be documented.

aliases={}
    Replace a value by another using a dictionary of aliases.

multiple
    The keyword argument `multiple` is not available for ``bounding-box``.

    `True`: Ensure a list value. Turn input into a list if needed.

    `False`: Ensure a non-list value. Turn a list input as non-list if the
    list has only one element. Fails with ValueError if the list has more
    than one element.

    `None`: Accept list and non-list values without transformations.
