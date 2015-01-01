.. _iproperties:

======================
IProperties and ranges
======================

The IProperties are at the very heart of Eapii. The following sections will
detail a bit more the way they work and how they can be customized to fit your
need when their default behaviour does not. Ranges are not IProperties in
themselves but they are used in conjunction with them, and will be presented
in the last section.

.. contents::

IProperties
-----------

A property is a way to specify how an attribute can be got or set. IProperties
are custom properties designed to interact with instruments. The get and the 
set process are each split in three steps represented by three methods you can
customize : `pre_get`, `get` and `post_get`, and `pre_set`, `set` and 
`post_set`.
Actually, if caching is enabled, before doing anything the cache value is 
checked to avoid useless communication. Deleting can be used to clear the 
cache.

**Note :**
The whole get (set) operation is locked using a re-entrant lock to make it 
thread safe. The lock is stored on the driver under the `lock` attribute, and
be accessed under the same name for subsystems and channels.

IProperties must be declared at the class level like any other property.
The first two arguments of any IProperty are 'get' and 'set' which should be
given non None value if the IProperty is to be gettable and/or settable. The
use of additional arguments allows to provide default behaviour for the pre\_ 
and post\_ hooks.

By default the `get` and `set` method simply falls back on the 
`default_get_iproperty` and `default_set_iproperty` methods of the drivers,
which are implemented at the driver type level. Those methods get passed the
values passed for the 'get' and 'set' argument of the IProperty constructor.
In  the same way, `post_set` simply check that the operation did not result in 
any error by calling the  `default_check_instr_operation` method of the driver.
This method needs to be implemented for each driver. 

Implemented iproperties
^^^^^^^^^^^^^^^^^^^^^^^

- :py:class:`IProperty <eapii.core.iprops.i_property.IProperty>`:
	This is the most basic implementation. Two ways of customisation available
	to all other IProperty are available: you can ask to reattempt a get or a 
	set operation if it fails due to a communication error (secur_com argument)
	, or ask to perform a number of checks before getting or setting the state
	of the instrument (checks argument).

- :py:class:`Unicode <eapii.core.iprops.scalars.Unicode>`:
	This IProperty casts the value returned by the instrument to a unicode 
	string. The acceptable values can also be specified using the 'values'
	argument.

- :py:class:`Int <eapii.core.iprops.scalars.Int>`:
	This IProperty casts the value returned by the instrument to a integer.
	The acceptable values can be specified using the 'values' argument or
	specifying a range of acceptable value.

- :py:class:`Float <eapii.core.iprops.scalars.Float>`:
	This IProperty casts the value returned by the instrument to a float.
	The acceptable values can be specified using the 'values' argument or
	specifying a range of acceptable value. Additionally the unit in which the
	value should be expressed can be specified as a string, in which case all
	values will be returned as Quantity (see Pint library) and when setting
	if the value is provided as a Quantity it is automatically converted to
	the right unit, if a simple float is provided it is assumed to be already
	be expressed in the right unit.

- :py:class:`Mapping <eapii.core.iprops.mappings.Mapping>` :
	This IProperty is used to provide user friendly values when the instrument
	uses for example integer based enumeration. When getting the value 
	the instrument answer is converted using the mapping before being returned.
	When setting the value is converted to the instrument representation 
	before being passed to the set method.

- :py:class:`Bool <eapii.core.iprops.mapping.Bool>`:
	Bool is a specialised mapping used for boolean values. The answer is always
	returned as a bool but aliases can be declared to allow using non-boolean
	values when setting. For example, the output state of an instrument
	declared as a bool can be made to accept 'On' and 'Off' as acceptable
	values.

- :py:class:`Register <eapii.core.iprops.register.Register>`:
	Register is a special Mapping used to translate a byte registry to a
	dictionary whose values represent the state of the associated bit.
	Values can be either accessed by name or index.

Customisation hooks
^^^^^^^^^^^^^^^^^^^



Ranges
------



