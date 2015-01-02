.. _runtime_tweaking:

================
Runtime tweaking
================

.. contents::

Default driver behaviours are all encoded in the class definition. However
as some use cases might require different behaviour Eapii allows to alter those
default. The two main cases are presented in the following.

Caching permissions
-------------------

To avoid unnecessary communications, Eapii cache a number of instruments
parameters by default. If in a particular situation this behaviour is not
desired, caching can be deactivated by `passing caching_allowed=False` as
keyword argument to the driver constructor. This will prevent caching any
value. If only some values should not be cached, or on the contrary should be,
one can pass a dictionary containing the authorisation as boolean using the
keyword argument `caching_permissions`.

**Note :**

As Eapii ensures that only a single driver can exist at a time for a single
instrument creating a new driver can result in getting a reference to an
existing one. If such a thing occurs all keywords argument are ignored, so
no caching customisation is performed. You can check whether or not the driver
was actually created by asserting the value of the `newly_created` attribute.

IProperty patching
------------------

Another way  to alter the runtime behaviour of a driver is to patch an
IProperty. By patching an iproperty through the `patch_iprop` method, you can
change any attribute even if the main use is to replace one of the following
method : pre_get, get, post_get, pre_set, set, post_set. The following syntax
can be used for a driver, a subsystem or a channel :

    >>> func = lambda iprop, driver, value : 2*value
    >>> d.patch_iprop('post_get', func)

This operation can be reverted using `unpatch_iprop` and the name of the
patched attribute or `unpatch_all` if all runtime patch are to be removed.
