.. _configuration:

=============
Configuration
=============

.. contents::

Eapii has some global settings related to its use of external librairies. Most
of the time the default values should be fine. However if it is not the case
the following sections describe how to provide custom parameters.

**Note :**

Those customisations must always take place before Eapii falls back to its
default behaviour. So the following procedures should be used before importing
and instantiating any driver.

Using a non-default UnitRegistry
--------------------------------

Eapii uses `Pint`_ to handle units. Pint uses a UnitRegistry to hold all the unit
definitions and convert Quantity between them, but can only deal with units
defined on the same registry.

By default Eapii creates a UnitRegistry when it first needs it and use it for
all operations. As explained in :ref: `basic_usage`, you can access it in the
following way :

    >>> from eapii.core import unit
    >>> unit.get_unit_registry()

If for any reason you need to use a custom unit registry, you should use the
`set_unit_registry` function of the eapii.core.unit module, to set it. You can
do this only once before Eapii creates the default one.

.. _Pint: http://pint.readthedocs.org/en

Selecting the PyVISA backend
----------------------------

As of version 1.6, `PyVISA`_ supports multiple backends. By default when it
first needs it, Eapii creates a default ResourceManager connected to the 'ni'
backend which relies on a visa dll for communication.

You can select a different one by using the function `set_visa_resource_manager`
found in the eapii.visa.visa module. This function accepts the same arguments
as ResourceManager or alternatively can be passed an already instantiated
ResourceManager.

**Note :**
Pyvisa supports creating multiple RessourceManager connected to different
backends. For the time being, Eapii supports using only a single one at a time.
This might evolves in the future though.

.. _PyVISA: http://pyvisa.readthedocs.org
