.. _basic_usage:

===========
Basic usage
===========

Eapii can be used in large applications or in an interactive prompt. The
following sections cover the very steps in using Eapii. It apllies to both
usage.


Finding a driver
----------------

Eapii has some introspection capabalities allowing to automatically discovers
and lists the known drivers and driver types. (NB : a driver type refers to
a genric kind of driver defining how the communication with the instrument is
done).

The functions needed are located in the eapii.explore module :

- list_drivers():
    This function returns the list of the names of all known drivers.

- list_driver_types():
    This function returns the list of the names of all known driver types.

- get_driver(name):
    Retrieve the class for a driver given its name.

- get_driver_types(name):
    Retrieve the class for a driver type given its name.

If any of these operations encounter a problem it will log it and also store
it. You can then use the following functions to try to understand what went
wrong :

- loading_errors():
    Return a dictionary containing the module in which the error happened as
    key and the message as value.

- print_loading_errors():
    Format and print the errors which happened during loading.

Opening the connection
----------------------

Every driver, independently of its type, expects on instantiation at least one
argument which is a dictionary containing the different informations necessary
to open the connection to the instrument. Once instantiated the driver is
automatically connected to the instrument (this behaviout can be moified by
passing auto_open=False to the constructor). From there you can simply retrieve
or set the value of the instrument parameters like any other attributes.

    >>> d = Instrument({'address': 1})
    >>> d.value
    <<< 1
    >>> d.value = 2

At any moment you can close the connection using `close_connection`, or reopen
it using `reopen_connection`. Once closed the connection can be opened anew
using `open_connection`. To check whether or not the driver is connected check
the value of the `connected` attribute.


Unit handling
-------------

Units are handled using the `Pint` library. All unit definition are stored in
a unit registry. To access the registry used by Eapii, simply call
`get_unit_registry` which you can import from eapii.core.api. If you need to
use a special unit registry please look at :ref: `configuration` for how to do
this.

You can use any compatible unsit when setting a driver IProperty, however the
driver will always answer in its base unit. You can easily convert the returned
value using in the following way :

    >>> d.voltage
    <<< 0.1 V
    >>> d.voltage.to('mV')
    >>> 10 mV

.. _Pint: http://pint.readthedocs.org/en

Errors
------

Eapii tries to raise meaningful errors when anything goes wrong. Besides
standard ValueError or TypeError there are two main types of errors Eapii can
raise :

- InstrError :
    Generic error related to an instrument.

- InstrIOError :
    Error related to an issue in communicating with the instrument.


Cache cleaning
--------------

If for any reason you need to clean the cache of an instrument you can use
the `clear_cache` methods. By default it will clear the cache of the instrument
and all its subsystems and/or channels. Using the 'properties' keyword a list
of attributes to clear can be specified, dotted names can be used to access the
cache of subsytems and channels. (NB: all channels are treated in the same way
independently of its ID).

You can also consult the cache state using the `check_cache` method.
