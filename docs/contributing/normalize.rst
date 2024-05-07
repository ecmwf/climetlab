.. _normalize:

Normalize decorator
===================

This section discusses :ref:`the purpose <purpose_normalize>` of the `@normalize` decorator,
shows :ref:`how to use it <howto-normalizer>` and provides the :ref:`reference documentation <reference_normalize>`.

.. _purpose_normalize:

Purpose (discussion)
--------------------

When sharing code, a large amount of code is usually
dedicated to processing the arguments of the functions
or methods to check their value and normalize it to a
standard format.

The Python language offers the ability to accept a large
range of input type on a unique function through `duck typing`.
This leads to better integration of the different objects
at stake, for instance using an object such as ``xarray.Dataset``
or a ``pandas.DataFrame`` or ``pandas.Serie`` as input
to provide a list of dates.


CliMetLab offers predefined shortcuts to
implement this. The short API aims to address 80% of
the use cases using the ``@normalize`` decorator.
The longer form aims to tackle specific needs.

Compare the following codes snippets:


.. dropdown:: Boilerplate code
    :open:

    Tedious and error-prone Python code is needed to check
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
            (more checks and transformations)
            (...)
            do_stuff(date, option)


.. dropdown:: Using CliMetLab short form API
    :open:

    The decorator `@normalize` provides generic default behaviour
    to handle domain-specific arguments (for dates, meteorological and climate
    parameters, bounding boxes, etc.)

    .. code-block:: python

        from climetlab.decorators import normalize
        @normalize("date","date(%Y%m%d)")
        @normalize("option",["foo", "bar"])
        def __init__(self, date, option):
            do_suff(date, option)


.. _howto-normalizer:

How to use
----------

- How to ensure that the value in the function belongs to a list?

    .. literalinclude:: normalize-example-enum.py


- How to ensure that the value in the function is a date
  with this format "YYYY-MM-DD"?

    .. literalinclude:: normalize-example-date.py

- How to ensure that the value in the function is a list?

   Add the keyword argument ``multiple=True``.
   Not available for ``bounding-box``.

- How to ensure that the value in the function is a list of int?

    .. literalinclude:: normalize-example-int.py

- How to ensure that the value in the function is not a list?

    Add the keyword argument ``multiple=False``.

- How to accept list or non-list as input?

    Add the keyword argument ``multiple=None``.
    Not available for ``bounding-box``.


- How to add alias/shortcuts/special values to be replaced by actual
  predefined values?

    Use the keyword argument ``alias`` and provide a dictionary.

    .. literalinclude:: normalize-example-alias.py

    .. literalinclude:: normalize-example-alias-2.py


.. _reference_normalize:

Reference
---------

.. warning::

    This API is experimental, things may change.


``@normalize(name, values, aliases={}, multiple=None, **kwargs)``

The ``@normalize`` decorator transforms the arguments provided when calling
the decorated function, modifies it if needed, and provides a normalised
value to the function. It ensures that the value of the argument is what
is expected to be processed by the function.


values
    If `values` is a list, the list provides allowed values for the parameter.
    If `values` is a string, it is expected to be a shortcut similar to
    `"type(options)"` where `type` is one of the following: ``"date"``, ``"date-list"``,
    ``"bounding-box"``.
    These shorts cut aims at providing an easy way to define many options in
    a more concise manner.

    Example: ``"date-list(%Y%m%d)"``

type
    Type of value expected by the function. The type should be one of the
    following: ``"str"``, ``"int"``, ``"float"``, ``"date"``, ``"date-list"``,
    ``"str-list"``, ``"int-list"``, ``"float-list"``.


format
    The keyword argument `format`
    is available for `type`
    ='date' and
    'date-list'.
    It provides the expected format according to `datetime.strftime`.
    Example: format='%Y%m%d'

convention
    Experimental. To be documented.

aliases
    Replace a value with another using a dictionary of aliases.

multiple
    The keyword argument `multiple` is not available for ``bounding-box``.

    `True`: Ensure a list value. Turn input into a list if needed.

    `False`: Ensure a non-list value. Turn a list input as non-list if the
    list has only one element. Fails with ValueError if the list has more
    than one element.

    `None`: Accept list and non-list values without transformations.


.. todolist

    Examples
    --------

    ..  todo::
        Add example from tests.
