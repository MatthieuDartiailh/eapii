# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------

""" HasIProp is the most basic object in Eapii.

It handles the use of IProperty, Subsystem, and Channel and the possibility
to customize IProperty behaviour by defining specially named methods.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from future.utils import with_metaclass, bind_method
from inspect import getmembers
from types import FunctionType, MethodType
from functools import update_wrapper

from .iprops.i_property import IProperty

# Prefixes for IProperty specially named methods.
POST_GET_PREFIX = '_post_get_'
GET_PREFIX = '_get_'
PRE_SET_PREFIX = 'pre_set_'
SET_PREFIX = '_set_'
POST_SET_PREFIX = '_post_set_'

CUSTOMIZABLE = ((POST_GET_PREFIX, 'get'), (GET_PREFIX, 'get'),
                (PRE_SET_PREFIX, 'pre_set'), (SET_PREFIX, 'set'),
                (POST_SET_PREFIX, 'post_set'))


# Delayed import functions
def _subsystem():
    from .subsystem import Subsystem
    return Subsystem


def _channel():
    from .channel import Channel
    return Channel


def wrap_custom_iprop_methods(cls, meth_name, iprop):
    """ Wrap a HasIProp method to make it an instance method of a IProperty.

    This is necessary so that users can define overriding method in a natural
    way in the HasIProp subclass assuming that the instance object will be
    passed as first argument and the IProperty object as second when in reality
    it will be the other way round due to python binding mechanism.

    Parameters
    ----------
    cls : type
        Class on which the method which should override the default behaviour
        of the IProperty is defined.
    meth_name : unicode
        Name of the method which should be used to override the default
        behaviour of the IProperty.
    iprop : IProperty
        Instance of IProperty whose default behaviour should be overridden.

    Returns
    -------
    wrapped : MethodType
        Method object which can be

    """
    wrapped = getattr(cls, meth_name)

    def wrapper(iprop, instance, *args, **kwargs):
        return wrapped(instance, iprop, *args, **kwargs)

    update_wrapper(wrapper, wrapped)
    return MethodType(wrapper, iprop)


def channel_getter_factory(cls, name, ch_cls):
    """ Factory function returning custom builder for channel instances.

    The factory function is bound to the calling class.

    Parameters
    ----------
    cls : type
        Class to which bind the channel getter method.
    name : unicode
        Name of the channel, used for caching and naming purposes.
    ch_cls : type
        Class of the channel used for instantiation.

    Return
    ------
    Bound

    """
    def channel_getter(self, ch_id):
        return self._generic_get_channel(name, ch_cls, ch_id)

    f_name = 'get_' + name
    channel_getter.__name__ = f_name
    setattr(cls, f_name, bind_method(cls, f_name, channel_getter))


class AbstractHasIProp(object):
    """ Sentinel class for the collections of IProperties.

    """
    pass


class HasIPropsMeta(type):
    """ Metaclass handling IProperty customisation, subsystems registration...

    """
    def __new__(meta, name, bases, dct):

        # Pass over the class dict once and collect the information
        # necessary to implement the various behaviours.
        iprops = {}                 # IProperty declarations
        subsystems = {}             # Subsystem declarations
        channels = {}               # Channels declaration
        post_get = []               # Post get methods: _post_get_*
        iget = []                   # Get methods: _get_*
        pre_set = []                # Pre set methods: _pre_set_*
        iset = []                   # Set methods: _set_*
        post_set = []               # Post set methods: _post_set_*

        subsystem_type = _subsystem()
        channel_type = _channel()

        for key, value in dct.iteritems():
            if isinstance(value, IProperty):
                iprops[key] = value
                value.set_name(key)
            elif isinstance(value, subsystem_type):
                subsystems[key] = value
            elif isinstance(value, channel_type):
                channels[key] = value
            elif isinstance(value, FunctionType):
                if key.startswith(POST_GET_PREFIX):
                    post_get.append(key)
                elif key.startswith(PRE_SET_PREFIX):
                    pre_set.append(key)
                elif key.startswith(POST_SET_PREFIX):
                    post_set.append(key)
                elif key.startswith(GET_PREFIX):
                    iget.append(key)
                elif key.startswith(SET_PREFIX):
                    iset.append(key)

        # Create the class object.
        cls = type.__new__(meta, name, bases, dct)

        # Walk the mro of the class, excluding itself, in reverse order
        # collecting all of the iprops into a single dict. The reverse
        # update preserves the mro of overridden iprops.
        base_iprops = {}
        for base in reversed(cls.__mro__[1:-1]):
            if base is not AbstractHasIProp \
                    and issubclass(base, AbstractHasIProp):
                base_iprops.update(base.__iprops__)

        # The set of iprops which live on this class as opposed to a
        # base class. This enables the code which hooks up the various
        # static behaviours to only clone a iprops when necessary.
        owned_iprops = set(iprops.keys())

        # Add the special statically defined behaviours for the iprops.
        # If the target iprop is defined on a parent class, it is cloned
        # so that the behaviour of the parent class is not modified.
        all_iprops = dict(base_iprops)
        all_iprops.update(iprops)

        def clone_if_needed(ip):
            if ip not in owned_iprops:
                ip = ip.clone()
                all_iprops[ip.name] = ip
                iprops[ip.name] = ip
                owned_iprops.add(ip)
                setattr(cls, ip.name, ip)
            return ip

        def customize_iprops(cls, prefix, ip_meth):
            n = len(prefix)
            for mangled in post_get:
                target = mangled[n:]
                if target in all_iprops:
                    iprop = clone_if_needed(all_iprops[target])
                    wrapped = wrap_custom_iprop_methods(cls, mangled, iprop)
                    setattr(iprop, ip_meth, wrapped)

        for prefix, attr in CUSTOMIZABLE:
            customize_iprops(cls, prefix, attr)

        # Put a reference to the iprops dict on the class. This is used
        # by HasIPropsMeta to query for the iprops.
        cls.__iprops__ = iprops

        # Put a reference to the subsystems in the class.
        # This is used at initialisation to create the appropriate subsystems
        cls.__subsystems__ = subsystems

        # Create channel initialisation methods.
        if channels:
            cls.__channels__ = set(channels)
            for ch, cls in channels.items():
                channel_getter_factory(name, cls)

        return cls


class HasIProp(with_metaclass(HasIPropsMeta, object)):
    """ Base class for objects using the IProperties mechanisms.

    """
    def __init__(self, caching_allowed=True, caching_permissions={}):

        self._cache = {}
        self._range_cache = {}

        subsystems = self.__subsystems__

        if caching_allowed:
            # Avoid overriding class attribute
            perms = self.caching_permissions.copy()
            perms.update(caching_permissions)
            self._caching_permissions = set([key for key in perms
                                             if isinstance(perms[key], bool)
                                             and perms[key]])

            ss_cache_allowed = {k: bool(v) for k, v in perms.items()
                                if k in subsystems and v or isinstance(v,
                                                                       dict)}
            ss_caching = {k: v for k, v in perms.items()
                          if k in subsystems and isinstance(v, dict)}

        else:
            self._caching_permissions = set()
            ss_cache_allowed = {ss: False for ss in subsystems}

        for ss, cls in subsystems.items():
            subsystem = cls(self, ss_cache_allowed[ss], ss_caching.get(ss))
            setattr(self, ss, subsystem)

        if self.__channels__:
            self._channel_cache = {ch: {} for ch in self.__channels__}

    def get_range(self, range_id):
        """ Access the range object matching the definition.

        Parameters
        ----------
        range_id : str
            Id of the range to retrieve. The id should be the name of an
            IProperty identified as a range (initialized with the range
            keyword).

        Returns
        -------
        range_validator: RangeValidator
            A range validator matching the current attributes state, which can
            be used to validate either float (assuming it is expressed in the
            right unit) or a Quantity.

        """
        pass

    def discard_range(self, range_id):
        """ Remove a range from the cache.

        This should be called by methods of IProperty setters which for any
        reasons invalidate a range.

        Parameters
        ----------
        range_id : str
            Id of the range to retrieve. The id should be the name of an
            IProperty identified as a range (initialized with the range
            keyword).

        """
        pass

    def clear_cache(self, properties=None):
        """ Clear the cache of all the properties or only of the specified
        ones.

        The cache of subsystems and channels is left untouched by this method.

        Parameters
        ----------
        properties : iterable of str, optional
            Name of the properties whose cache should be cleared. All caches
            will be cleared if not specified.

        """
        test = lambda obj: isinstance(obj, IProperty)
        cache = self._cache
        if properties:
            for name, instr_prop in getmembers(self.__class__, test):
                if name in properties and name in cache:
                    del cache[name]
        else:
            self._cache = {}

    def check_cache(self, properties=None):
        """Return the value of the cache of the object.

        The cache values for the subsystems and channels are not accessible.

        Parameters
        ----------
        properties : iterable of str, optional
            Name of the properties whose cache should be cleared. All caches
            will be cleared if not specified.

        Returns
        -------
        cache : dict
            Dict containing the cached value, if the properties arg is given
            None will be returned for the field with no cached value.

        """
        test = lambda obj: isinstance(obj, IProperty)
        cache = {}
        if properties:
            for name, instr_prop in getmembers(self.__class__, test):
                if name in properties:
                    cache[name] = self._cache.get(name)
        else:
            cache = self._cache.copy()

        return cache

    def _generic_get_channel(self, name, ch_cls, ch_id):
        """ Generic implementation of the channel getter.

        This function manages the channel cache and is responsible for
        delivering to the user the channel object corresponding to the given
        id.

        Parameters
        ----------
        name : unicode
            Name of the channel. This the name of the class attribute used to
            define the channel. This argument is directly provided by the
            specific get_* channel method.
        ch_cls : type
            Class of the channel which should be created if necessary.
        ch_id :
            Object used to identified the channel this can typically be an
            integer or a string. In any case it should be hashable.

        Returns
        -------
        channel : Channel
            Channel instance bound to this object with the correct id.

        """
        ch_cache = self._channel_cache
        if name in ch_cache and ch_id in ch_cache[name]:
            return ch_cache[name][id]
        else:
            ch = ch_cls(self, ch_id)
            ch_cache[name][ch_id] = ch
            return ch
