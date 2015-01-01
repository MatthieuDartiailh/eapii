.. _backend_type:

.. _Eapii : htpp://github.com/MatthieuDartiailh/eapii/issues

============
Backend type
============

The first question you need to answer when writing a new driver is the
following : How will my computer communicate with my instrument ?

In most cases the answer is simply the VISA protocole (supported over GPIB,
USB, Ethernet, etc ...). If this your situation, you can directly go to the
`Visa`_ section. Other cases can include the following :

- the constructor ships alongside its instrument a library (.dll under Windows,
  .so under Linux) that you can use to communicate with your instrument. If so
  go to the `C library`_ section.

- the constructor has a Python interface for its instrument. If so go to the
  `Native python`_ section.

- if none of the previous cases apply you can open a ticket on `Eapii`_ github
  issue tracker or contact directly the developer.


Visa
----

This is the most common case, at least for major constructors products. Eapii
supports the use of the VISA protocole through the use of the PyVISA project.

Two standards of communication exists within VISA :

- One based on the exchange of text messages (the most common). It is supported
  on GPIB, USB, Ethernet. If so, your driver should inherit of
  VisaMessageInstrument. Most new instruments have adopted an additional
  standard known as IEC60488 and support a set of of common commands (\*IDN?,
  \*ESR, \*ESR?, look at `eapii.visa.standards` for the complete list of
  command). If so you should make your driver inherits from the `IEC60488`
  class (which is a subclass of VisaMessageInstrument).

- The other use a binary registry from which bytes are read or witten directly.
  They usually use PXI ports. If so your driver should inherit from
  `VisaRegisterInstrument`.


In both cases, Eapii wraps a number of useful attributes and methods from the
PyVISA object used for communication. Those are presented below. If for any
reason you need to access something else the PyVISA object is stored in the
private attribute `_driver`. In such a case please consider opening an issue on
`Eapii`_ issue tracker on Github.

**Note :**
Visa driver are expected to have a class attribute `protocoles` specifying the
mode to use for each type of connection under the form of a dictionary. This
allows to easily determine from the command the kind of connection supported
and its mode (most of the time it is trivial (INSTR) but when a raw socket
is used it is useful to know the port number without having to browse the docs
of the instrument) :

.. code-block :: python

    class VisaDriver(VisaMessageInstrument):

        protocoles = {'GPIB': 'INSTR', 'TCPIP': '50000::SOCKET'}

Message based instrument
^^^^^^^^^^^^^^^^^^^^^^^^

    - encoding :

    - write_termination :

    - read_termination :

    - write :

    - write_ascii_values :

    - write_binary_values :

    - write_values :

    - read :

    - read_values :

    - query :

    - query_ascii_values :

    - query_binary_values :

    - query_values :

    - assert_trigger :

    - status_byte :


Register based instruments
^^^^^^^^^^^^^^^^^^^^^^^^^^

    - read_memory :

    - write_memory :

    - move_in :

    - move_out :

C library
---------

Eapii plans to support wrapping external C libraries using CFFI (or ctypes)
starting at version 0.2. If you need this feature urgently please contact
the developper.

Native python
-------------

When a native Python support is provided by the vendor it can come in many
ways, so it is hard to give a single recipe. Here are some guidelines :

- the vendor python package should be imported in a single file

- any application wide ressource (such as a server) should be created only when
  needed and then cached in a module variable (look at eapii/visa/visa.py
  module for an example).

Feel free to contact the developper or open issue to get support in developping
such a driver.
