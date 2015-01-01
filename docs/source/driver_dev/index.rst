.. _driver_dev:

===================
Writing new drivers
===================

The following sections will guide you through the writing of a new driver using
Eapii. This section however cannot replace a detailed lecture of the instrument
manual, without which you will be unable to find the answer to most of the
question you will have to answer to write the driver.

First thing, you will have to determine what kind of communication your
instrument support which is the topic of the first section. The second will
help you determine whether or not it makes sense to decompose your driver
in subsystems and channels. Finally the third will present in details the
working of the iproperties and how to use them at their best to make your life
easy.

If you write a driver even partial for an instrument please consider
contribuing it to Eapii.

**Note : **
In order to Eapii to automatically detect your driver, you should declare a
module variable `DRIVERS` which should be a dictionary containing the name
of the instrument as key and the class as value.

.. code-block::
	
	class Driver(BaseInstrument):
		pass
		
	DRIVERS = {'Instrument_name': Driver}

.. toctree::

    backend_type
    subsystems_channels
    iproperties
