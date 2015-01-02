.. _introduction:

============
Introduction
============

.. contents::

Python is a highlevel language with a wide and active community in the world
of sciences, which makes it a natural choice for interfacing instruments and
automating experiments. However, most instrument fabricants does not provide
Python drivers for their products and writing one from scratch is a tedious job
if one wants to have, lets say, advanced features such as unit handling and
good operation control.

Eapii aims at making writing full featured instrument drivers easy, while
giving the developer the possibility to tweak almost every part of the driver
behaviour.

Inspirations
------------

A number of project are already trying to tackle those issues. However as I was
not completely convinced by the approach chosen by those I started my own
package. Eapii is strongly inspired from the Lantz project and the Slave
project, so people used to work with these ones might find a number of
similarities.

Eapii focus on the highest level of abstraction, and try as much as possible to
delegate the burden of the actual communication with the instrument to others.
For example the VISA protocol is supported through the use of the excellent
PyVISA project.

Eapii design is centred around two key points :
- the use of smart properties (IProperties) to give an easy, powerful and
natural access to the instrument parameters.
- the possibility to split a driver in multiple subsystems for clarity sake but
also because most complex instruments have a notion of channel that Eapii
supports natively.

IProperties
-----------

IProperties are standard Python properties which have been tweaked to make easy
to perform checks and others operation before and after getting and setting an
instrument value. Getting a value happens in three steps : first some checks
can be performed (pre_get method), then the value is retrieved (get method),
finally the value can be converted before being sent to the user (post_get
method). Setting a value follow a similar patten : the value is first converted
to an instrument representation (pre_set method), the value is then sent to the
instrument(set method), and finally the operation success is asserted (post_set
method). Any Iproperty can be marked for caching in which case the cache state
is checked before calling any of the previously mentioned methods.

Brief descriptions of the different IProperties subclasses and their default
behaviours :

- IProperty:
    Most basic implementation supports assertions before getting or setting a
    value and automatic check for errors.

- Unicode:
    IProperty simply casting instrument answers to unicode. The possibility to
    specify a set of allowed value has been added compared to IProperty.

- Int:
    IProperty casting instrument answers to integer and able to check when
    setting a value that it is in the right range or in a set of allowed
    values.

- Float:
    IProperty casting the instrument answer to a float. The validation methods
    available for the Int are also available. This IProperty can also handle
    Quantity object (through the use of the Pint library) which allow to
    specify the unit of the value.

- Mapping:
    IProperty using a dictionary to map user input to instrument understandable
    values. This is most useful when an instrument use integer values to
    specify a mode as the user don't need to know the meaning of the integer
    values and can simply work with the name of the mode.

- Bool:
    A special kind of mapping for boolean values. Aliases for True, and False
    can be declared to allow the use of, for example, 'ON' and 'OFF' as values
    when setting. However the answer to a get will always be a boolean.

- Register:
    A special kind of mapping to handle single byte answers. In this case the
    mapping is used to interpret the meaning of each bit.

**Notes**:
You can find more detailed informations about IProperties uses and internals in
the following sections :ref: `driver_dev`.

Driver modularity
-----------------

Save for the most simple instruments, it often makes sense to divide the driver
in several parts. Furthermore, some instruments have a notion of channel which
can either be only logical or refers to some hardware reality.

- Subsystems:
    A subsytem is used to break a driver in several logical part, it acts like
    a fullscale driver save that it pipes its commands to its 'parent' for the
    actual communication with the instrument.

- Channels:
    Channels are very similar to subsystem in that they also pipes their
    commands to their parent, however contrary to subsystem multiple channels
    of the same type can exist for the same driver. This is possible because
    a channel has an ID which is used to identify it and send the command to
    the right part of the instrument. Eapii automatically makes sure that only
    one channel is created per ID. To access a channel simply call the
    get_*channel name* method with the ID of the channel.

Caching safety and thread safety
--------------------------------

Eapii offers the possibility to cache a number of instruments parameters to
tries to limit the actual communication with the instrument. As this is
likely (and could even be dangerous) to generate a lot of confusion if multiple
drivers access to the same instrument, Eapii enforces the unicity of the
driver based on the communication information. This could produce unexpected
behaviour when customizing instances, please see the :ref: `driver_dev` section for more
details.

Eapii tries to make your code thread safe by using a lock around every get or
set operation which means you easily drivers in parallel multiple instruments
using threads. The lock, stored in the lock attribute, is re-entrant so you can
manually lock larger operations if necessary. Note also that a single lock
exists per driver but can be accessed from any subsystem or channel.


