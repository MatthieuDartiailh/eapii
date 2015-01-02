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

The previously mentioned IProperties should cover a majority of use case, but 
sometimes they won't be sufficient because your instrument is odd. In this case
you can customize any step of the getting or setting process by creating a
method on the driver with a name of the form _{step name}_{iprop name} (ex :
for an iproperty named 'power' you could write a method _pre_set_power).

The arguments are the same that the ones of the IProperty method you are 
overriding save for the fact that the order of the iproperty and the driver 
instance are reversed (as it is a method of the driver).

**Note :**
When you override the behaviour of an IProperty it is your responsibility
to make sure that the automatic behaviour are still working. Let's say you 
override the post_get behaviour of an Int, if you still want to get an int
as the return value you must do the conversion yourself. As you also chose
the IProperty parameters you know what it should do and as IProperties
provide methods to do their standard work, it is not too hard to get it right.

Here is a brief list of what each hook is intended to be used for :

- pre_get :
	Called before attempting to retrieve a value from the instrument. Its main
	purpose is to run check to validate that the operation makes sense given 
	the state of the instrument. This is where `checks` get validation happens.

- pre_set :
	Called before attempting to set the instrument state. It can be used to
	check the instrument state, or the value validity and to preprocess the 
	value to make it understandable to the instrument.		

- get :
	This method should simply retrieve the instrument state and return it. It
	is not meant to be used for conversions. By default it simply calls the
	`default_get_iproperty` method of the driver.

- set :
	This method should simply transmit the order to the instrument. By default 
	it simply calls the `default_set_iproperty` method of the driver.

- post_get :
	This method receives the return value from the get method. Its main purpose
	is to perform conversion to make the instrument answer more user friendly.

- post_set :
	This method is meant to allow to check that the instrument did perform the
	expected action. If an issue is detected an exception should be raised. 
	By default it simply calls the 
	`default_check_instr_operation` method of the driver.

	
Ranges
------

There is no Range IProperty which may seem strange at first. The reason is 
actually quite simple : instruments have not a single way to define a range.
In some cases, it is better to use a float, in other a mapping perhaps.
However one common need it to be able to check that a value is valid for the 
instrument ins its current state.

Eapii tackles this issue by allowing the user to declare a range validator 
for an IProperty (Int or Float). This validator can either be declared
statically using one of the class found in :py:mod:`eapii.core.range` or using
a  string. The first option makes sense for hardware limitations, the second
for value depending on some setting of the instrument. 

Eapii tries to do a lot of magic for you but it cannot guess a range from only
a string. Actually for each range you want to use (whose name can match an
existing IProperty), you must define a _range_{range name} method which must
return the range validator.

For efficiency range validators are cached. They can be retrieved using the
:py:meth:`get_range <eapii.core.has_i_props.HasIProps.get_range>` method and
cleared using the 
py:meth:`discard_range <eapii.core.has_i_props.HasIProps.discard_range` 
method. For every IProperty invalidating a range you must discard it in the
post_set method of that IProperty (for the time being no automatic way is 
provided to do so you must write a custom _post_set_* method).
