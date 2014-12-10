# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" HasIProp is the most basic object in Eapii.

It handles the use of IProperty, Subsystem, and Channel and the possibility
to customize IProperty behaviour by defining specially named methods.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from future.utils import with_metaclass, bind_method
from types import FunctionType, MethodType
from functools import update_wrapper
from inspect import cleandoc, getsourcelines
from textwrap import fill
from abc import ABCMeta
from collections import defaultdict

from .iprops.i_property import IProperty
from .iprops.proxies import make_proxy

# Prefixes for IProperty specially named methods.
POST_GET_PREFIX = '_post_get_'
GET_PREFIX = '_get_'
PRE_SET_PREFIX = '_pre_set_'
SET_PREFIX = '_set_'
POST_SET_PREFIX = '_post_set_'

CUSTOMIZABLE = ((POST_GET_PREFIX, 'post_get'), (GET_PREFIX, 'get'),
                (PRE_SET_PREFIX, 'pre_set'), (SET_PREFIX, 'set'),
                (POST_SET_PREFIX, 'post_set'))

RANGE_PREFIX = '_range_'


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
    # In Python 2 needs the cast as we use unicode_litterals
    channel_getter.__name__ = str(f_name)
    bind_method(cls, f_name, channel_getter)


class AbstractHasIProp(with_metaclass(ABCMeta, object)):
    """Sentinel class for the collections of IProperties.

    """
    pass


class AbstractSubSystem(with_metaclass(ABCMeta, object)):
    """Sentinel for subsystem identification.

    """
    pass


class AbstractChannel(with_metaclass(ABCMeta, object)):
    """Sentinel class for channel identification.

    """
    pass


class HasIPropsMeta(type):
    """ Metaclass handling IProperty customisation, subsystems registration...

    """
    def __new__(meta, name, bases, dct):

        # Create the class object.
        cls = super(HasIPropsMeta, meta).__new__(meta, name, bases, dct)

        # Pass over the class dict once and collect the information
        # necessary to implement the various behaviours.
        iprops = {}                     # IProperty declarations
        subsystems = {}                 # Subsystem declarations
        channels = {}                   # Channels declaration
        cust_iprops = {'get': [],       # Get methods: _get_*
                       'post_get': [],  # Post get methods: _post_get_*
                       'pre_set': [],   # Pre set methods: _pre_set_*
                       'set': [],       # Set methods: _set_*
                       'post_set': []   # Post set methods: _post_set_*
                       }
        ranges = []

        for key, value in dct.iteritems():
            if isinstance(value, IProperty):
                iprops[key] = value
                value.name = key
            # We check first channels as they are also subsystems
            elif isinstance(value, type):
                if issubclass(value, AbstractChannel):
                    channels[key] = value
                    if not value.secure_com_exceptions:
                        value.secure_com_exceptions = cls.secure_com_exceptions
                elif issubclass(value, AbstractSubSystem):
                    subsystems[key] = value
                    if not value.secure_com_exceptions:
                        value.secure_com_exceptions = cls.secure_com_exceptions
            elif isinstance(value, FunctionType):
                if key.startswith(POST_GET_PREFIX):
                    cust_iprops['post_get'].append(key)
                elif key.startswith(PRE_SET_PREFIX):
                    cust_iprops['pre_set'].append(key)
                elif key.startswith(POST_SET_PREFIX):
                    cust_iprops['post_set'].append(key)
                elif key.startswith(GET_PREFIX):
                    cust_iprops['get'].append(key)
                elif key.startswith(SET_PREFIX):
                    cust_iprops['set'].append(key)
                elif key.startswith(RANGE_PREFIX):
                    ranges.append(key)

        # Analyse the source code to find the doc for the defined IProperties.
        if iprops:
            lines, _ = getsourcelines(cls)
            doc = ''
            for line in lines:
                l = line.strip()
                if l.startswith('#:'):
                    doc += ' ' + l[2:].strip()
                elif ' = ' in l:
                    name = l.split(' = ', 1)[0]
                    if name in iprops:
                        iprops[name].__doc__ = fill(doc.strip(), 79)
                        doc = ''

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
            if ip.name not in owned_iprops:
                ip = ip.clone()
                all_iprops[ip.name] = ip
                iprops[ip.name] = ip
                owned_iprops.add(ip)
                setattr(cls, ip.name, ip)
            return ip

        def customize_iprops(cls, iprops, prefix, ip_meth):
            n = len(prefix)
            for mangled in iprops:
                target = mangled[n:]
                if target in all_iprops:
                    iprop = clone_if_needed(all_iprops[target])
                    wrapped = wrap_custom_iprop_methods(cls, mangled, iprop)
                    setattr(iprop, ip_meth, wrapped)
                else:
                    mess = cleandoc('''{} has no IProperty {} whose behaviour
                                    can be customised''')
                    raise AttributeError(mess.format(cls, target))

        for prefix, attr in CUSTOMIZABLE:
            customize_iprops(cls, cust_iprops[attr], prefix, attr)

        # Put a reference to the iprops dict on the class. This is used
        # by HasIPropsMeta to query for the iprops.
        cls.__iprops__ = iprops

        # Put a reference to the subsystems in the class.
        # This is used at initialisation to create the appropriate subsystems
        cls.__subsystems__ = subsystems

        # Keep a ref to names of the declared ranges accessors.
        cls.__ranges__ = set([r[7:] for r in ranges])

        # Create channel initialisation methods.
        cls.__channels__ = set(channels)
        for ch, ch_cls in channels.items():
            channel_getter_factory(cls, ch, ch_cls)

        return cls


class HasIProps(with_metaclass(HasIPropsMeta, object)):
    """ Base class for objects using the IProperties mechanisms.

    """

    caching_permissions = {}
    secure_com_exceptions = ()

    def __init__(self, caching_allowed=True, caching_permissions={}):

        self._cache = {}
        self._range_cache = {}
        self._proxies = {}

        subsystems = self.__subsystems__
        channels = self.__channels__

        if caching_allowed:
            # Avoid overriding class attribute
            perms = self.caching_permissions.copy()
            perms.update(caching_permissions)
            self._caching_permissions = set([key for key in perms
                                             if isinstance(perms[key], bool)
                                             and perms[key]])

            ss_cache_allowed = {ss: bool(perms.get(ss)) for ss in subsystems}

            ss_caching = {k: v for k, v in perms.items()
                          if k in subsystems and isinstance(v, dict)}

            self._ch_cache_allowed = {ch: bool(perms.get(ch))
                                      for ch in channels}

            self._ch_caching = {k: v for k, v in perms.items()
                                if k in channels and isinstance(v, dict)}

        else:
            self._caching_permissions = set()
            ss_cache_allowed = {ss: False for ss in subsystems}
            ss_caching = {}

            self._ch_cache_allowed = {ch: False for ch in channels}
            self._ch_caching = {}

        for ss, cls in subsystems.items():
            subsystem = cls(self, caching_allowed=ss_cache_allowed[ss],
                            caching_permissions=ss_caching.get(ss, {}))
            setattr(self, ss, subsystem)

        if self.__channels__:
            self._channel_cache = {ch: {} for ch in self.__channels__}

    def get_iprop(self, name):
        """ Acces the iprop matching the given name.

        Parameters
        ----------
        name : unicode
            Name of the IProperty to be retrieved

        Returns
        -------
        iprop : IProperty
            Matching IProperty object

        """
        return getattr(self.__class__, name)

    @property
    def declared_ranges(self):
        """Set of declared ranges for the class.

        Ranges are considered declared as soon as a getter has been defined.

        """
        return self.__ranges__

    def get_range(self, range_id):
        """Access the range object matching the definition.

        Parameters
        ----------
        range_id : str
            Id of the range to retrieve. The id should be the name of an
            IProperty identified as a range (initialized with the range
            keyword).

        Returns
        -------
        range_validator: AbstractRangeValidator
            A range validator matching the current attributes state, which can
            be used to validate values.

        """
        if range_id not in self._range_cache:
            self._range_cache[range_id] = getattr(self,
                                                  RANGE_PREFIX+range_id)()

        return self._range_cache[range_id]

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
        if range_id in self._range_cache:
            del self._range_cache[range_id]

    def patch_iprop(self, iprop, **kwargs):
        """Modify the behaviour of an iproperty for the current instance.

        This is achieved by creating a proxy on the IProperty linked to that
        instance. NB : when overriding a method the function used should take
        as first argument the iprop and as second th HasIProps object, no
        automatic wrapping is performed.

        Parameters
        ----------
        iprop : unicode
            Name of the IProperty whose behaviour should be overridden.
        **kwargs :
            Attributes of the IProperty to override in the proxy.

        """
        if not hasattr(self, '_proxied'):
            self._proxied = []

        i_p = getattr(type(self), iprop)
        if self not in i_p._proxies:
            make_proxy(i_p, self, kwargs)
            self._proxied.append(i_p)

        else:
            proxy = i_p._proxies[self]
            proxy.patch(kwargs)

    def unpatch_iprop(self, iprop, *args):
        """Restore the behaviour of an IProperty to its default.

        This is achieved by replacing the attributes by the ones of the proxy.
        If the proxy comes back to the iprop behaviour it is discarded.

        Parameters
        ----------
        iprop : unicode
            Name of the IProperty whose behaviour should be overridden.
        *args : optional
            Names of the attributes which should be restored. If omitted the
            proxy will be removed.

        Raises
        ------
        KeyError :
            If no proxy exists for the given IProp.

        """
        i_p = getattr(type(self), iprop)
        if self not in i_p._proxies:
            raise KeyError('No proxy found for {}'.format(iprop))

        if not args:
            del i_p._proxies[self]
            self._proxied.remove(i_p)
        else:
            proxy = i_p._proxies[self]
            proxy.unpatch(args)
            if proxy.obsolete:
                del i_p._proxies[self]
                self._proxied.remove(i_p)

    def unpatch_all(self):
        """Restore all IProperties behaviour to their default one.

        The class overidden behaviour are of course preserved.

        """
        for iprop in self._proxied:
            del iprop._proxies[self]

        self._proxied = []

    def clear_cache(self, subsystems=True, channels=True, properties=None):
        """ Clear the cache of all the properties or only of the specified
        ones.

        Parameters
        ----------
        subsystems : bool, optional
            Whether or not to clear the subsystems. This argument is used only
            if properties is None.
        channels : bool, optional
            Whether or not to clear the channels. This argument is used only
            if properties is None.
        properties : iterable of str, optional
            Name of the properties whose cache should be cleared. Dotted names
            can be used to access subsystems and channels. When accessing
            channels the cache of all instances is cleared. All caches
            will be cleared if not specified.

        """
        cache = self._cache
        if properties:
            sss = defaultdict(list)
            chs = defaultdict(list)
            for name in properties:
                if '.' in name:
                    aux, n = name.split('.', 1)
                    if aux in self.__subsystems__:
                        sss[aux].append(n)
                    else:
                        chs[aux].append(n)
                elif name in cache:
                    del cache[name]

            for ss in sss:
                getattr(self, ss).clear_cache(properties=sss[ss])

            if self.__channels__:
                for ch in chs:
                    for o in self._channel_cache.get(ch, {}).values():
                        o.clear_cache(properties=chs[ch])
        else:
            self._cache = {}
            if subsystems:
                for ss in self.__subsystems__:
                    getattr(self, ss).clear_cache(channels=channels)
            if channels and self.__channels__:
                for chs in self._channel_cache.values():
                    for ch in chs.values():
                        ch.clear_cache(subsystems)

    def check_cache(self, subsystems=True, channels=True, properties=None):
        """Return the value of the cache of the object.

        The cache values for the subsystems and channels are not accessible.

        Parameters
        ----------
        subsystems : bool, optional
            Whether or not to include the subsystems caches. This argument is
            used only if properties is None.
        channels : bool, optional
            Whether or not to include the channels caches. This argument is
            used only if properties is None.
        properties : iterable of str, optional
            Name of the properties whose cache should be cleared. All caches
            will be cleared if not specified.

        Returns
        -------
        cache : dict
            Dict containing the cached value, if the properties arg is given
            None will be returned for the field with no cached value.

        """
        cache = {}
        if properties:
            sss = defaultdict(list)
            chs = defaultdict(list)
            for name in properties:
                if '.' in name:
                    aux, n = name.split('.', 1)
                    if aux in self.__subsystems__:
                        sss[aux].append(n)
                    else:
                        chs[aux].append(n)
                elif name in self._cache:
                    cache[name] = self._cache[name]

            for ss in sss:
                cache[ss] = getattr(self, ss).check_cache(properties=sss[ss])

            if self.__channels__:
                for ch in chs:
                    ch_cache = {}
                    cache[ch] = ch_cache
                    for ch_id, o in self._channel_cache.get(ch, {}).items():
                        ch_cache[ch_id] = o.check_cache(properties=chs[ch])
        else:
            cache = self._cache.copy()
            if subsystems:
                for ss in self.__subsystems__:
                    cache[ss] = getattr(self, ss)._cache.copy()

            if channels:
                for chs, ch_dict in self._channel_cache.items():
                    ch_cache = {}
                    cache[chs] = ch_cache
                    for ch in ch_dict:
                        ch_cache[ch] = ch_dict[ch]._cache.copy()

        return cache

    def reopen_connection(self):
        """Reopen the connection to the instrument.

        """
        message = fill(cleandoc(
            '''This method is used to reopen a connection whose state
            is suspect, for example the last message sent did not
            go through, and should be implemented by classes
            subclassing HasIProps'''),
            80)
        raise NotImplementedError(message)

    def default_get_iproperty(self, cmd, *args, **kwargs):
        """Method used by default by the IProperty to retrieve a value from an
        instrument.

        Parameters
        ----------
        cmd :
            Command used by the implementation to determine what should be done
            to get the answer from the instrument.
        *args :
            Additional arguments necessary to retrieve the instrument state.
        **kwargs :
            Additional keywords arguments necessary to retrieve the instrument
            state.

        """
        mess = fill(cleandoc('''Method used by default by the IProperty to
            retrieve a value from an instrument. Should be implemented by
            classes subclassing HasIProps.'''), 80)
        raise NotImplementedError(mess)

    def default_set_iproperty(self, cmd, *args, **kwargs):
        """Method used by default by the IProperty to set an instrument value.

        Parameters
        ----------
        cmd :
            Command used by the implementation to determine what should be done
            to set the instrument state.
        *args :
            Additional arguments necessary to retrieve the instrument state.
        **kwargs :
            Additional keywords arguments necessary to retrieve the instrument
            state.

        """
        mess = fill(cleandoc('''Method used by default by the IProperty to
            set an instrument value. Should be implemented by
            classes subclassing HasIProps.'''), 80)
        raise NotImplementedError(mess)

    def default_check_instr_operation(self):
        """Method used by default by the IProperty to check the instrument
        operation.

        Returns
        -------
        result : bool
            Is everything ok ? Can we assume that the last operation succeeded.
        precision :
            Any precision about the situation, this can be any object but
            something should always be returned.

        """
        mess = fill(cleandoc('''Method used by default by the IProperty to
            check the instrument operation. Should be implemented by
            classes subclassing HasIProps.'''), 80)
        raise NotImplementedError(mess)

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
            return ch_cache[name][ch_id]
        else:
            ch = ch_cls(self, ch_id,
                        caching_allowed=self._ch_cache_allowed[name],
                        caching_permissions=self._ch_caching.get(name, {}))
            ch_cache[name][ch_id] = ch
            return ch

AbstractHasIProp.register(HasIProps)
