.. _subsystems_channels:

=================================================
Subsystems & channels : modularity in your driver
=================================================

One of Eapii key feature is the possibility to easily split in driver in
several parts. Whether or not you need to use channels should be fairly
straightforward : if your instrument either have internally a notion of
channel (let's say multiple acquisition channels, each having its own parameters
) or is composed of multiple cards to which you access through a single entry
point you should write a channel driver to access all the parameters specific
to the channel, the main driver being used only for the global parameters.
Using subsystems is less straightforward. Subsystems should be used to reflect
the logical organisation of your instrument and avoid using awfully long names.
One canonical example is the one of a lock-in : a lock-in is generally able to
generate a reference signal thanks to an internal oscillator, whose magnitude,
frequency and possibly other parameters can be adjusted. To avoid using
'oscillator_*' named iproperties which are heavy to use and tend to crowd the
instrument namespace, it makes sense to create an 'oscillator' subsystem to
group all its properties.

The two followings sections will detail the respective uses of channels and
subsystems.

Subsystems
----------

As mentioned earlier subsystems can be used to break a complex driver in more
mangeable parts. And this as many times as needed as subsystems can have
subsystems and even channels.

When writing a subsystem it should inherit from the Subsystem base class, in
this way all communication methods, used by the IProperties, are automatically
piped to the parent for execution allowing you to work as with a normal driver.
The parent driver is also stored in the parent attribute of the subsystem in
case you need to access it.

To declare a subsystem simply makes it a class attribute of your driver, Eapii
will then perform the magic to connect everything for you.

.. code-block:: python

    class Oscillator(Subsystem):
        """Here should go a description of the subsytem.

        """
        # And here the core of the driver, see the `iproperties`_ section for
        # more details about this part.

    class Instrument(BaseClass):
        # BaseClass should be replaced by the base class you determined after
        # reading the `backend_type`_ section.

        osc = Oscillator()

Channels
--------

Channels differs from subsystems in that for a single channel declaration in
the driver multiple instances can exist, each having a different id (stored in
the `ch_id` attribute of the channel). You can declare your channel just as
your driver and Eapii will take care of creating the `get_{channel name}`
method for you. You can if you need to write this method yourself but be sure
to properly cache the already created channels to avoid duplicatas. However
you do need to write a method `list_{channel name}s` taking no argument and
returning the list of available channels.

.. code-block:: python

    class InstrChannel(Channel):
        """Here should go a description of the channel.

        """
        # And here the core of the driver, see the `iproperties`_ section for
        # more details about this part.

    class Instrument(BaseClass):
        # BaseClass should be replaced by the base class you determined after
        # reading the `backend_type`_ section.

        osc = InstrChannel()
