.. _availability:

Availability decorator
======================

.. todo::

    Not implemented yet


Purpose
-------

When sharing code, a large amount of code is usually dedicated to
processing the arguments of the functions or methods where users
are requesting data. This boilerplate code needs to check their
values and ensure that data is actually available. In case of
failure, it would be helpful to generate an appropriate error message
to the user, in order to help them understand why the call to the
function was not successful.

CliMetLab offers predefined shortcuts to implement this. The short
API aims to address the most common use cases using the ``@availability``
decorator.


Example:

.. code-block:: python

    @availability("availability.json")
    def func(date, option):
        do_stuff(date, option)




Usage
-----


Reference
---------
