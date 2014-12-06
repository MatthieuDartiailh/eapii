# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Proxies used to provide per instance variation of the IProperty behaviour.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from types import MethodType, FunctionType
from weakref import WeakKeyDictionary


from .i_property import get_chain, set_chain


class _ProxyManager(object):
    """Manager caching the custom class used for proxying the different types
    of IProperty.

    This class is not meant to be instantiated by user code.

    """
    def __init__(self):
        super(_ProxyManager, self).__init__()
        self._proxy_cache = {}

    def make_proxy(self, iprop, instance, kwargs):
        """Build a proxy for the given iprop.

        For each type of IProperty a new mixin Proxy type is created by mixing
        the IPropProxy class and the iprop class. This class is then cached and
        used to build to create the proxy instance.

        Parameters
        ----------
        iprop : IProperty
            Instance whose behaviour should be altered by the use of a proxy.
        instance : HasIProps
            Object for which the IProperty should have a peculiar behaviour.
        attrs : dict
            Dict containing the attributes whose values should be overriden.

        """
        iprop_class = type(iprop)
        if iprop_class not in self._proxy_cache:
            # Python 2 compatibility cast
            proxy = type(str(iprop_class.__name__+'Proxy'),
                         (IPropertyProxy, iprop_class), {})
            self._proxy_cache[iprop_class] = proxy

        return self._proxy_cache[iprop_class](iprop, instance, kwargs)


make_proxy = _ProxyManager().make_proxy
"""Build a proxy for the given iprop.

This used the singleton _ProxyManager instance to handle the caching of the
proxy classes.

"""


class IPropertyProxy(object):
    """Generic proxy for IProperty, used to get per HasIProps instance
    behaviour.

    Parameters
    ----------
    iprop : IProperty
        Instance whose behaviour should be altered by the use of a proxy.
    instance : HasIProps
            Object for which the IProperty should have a peculiar behaviour.
    attrs : dict
        Dict containing the attributes whose values should be overriden.

    """
    def __init__(self, iprop, instance, attrs):
        self._iprop = iprop
        # This is created now to avoid creating lots of those for nothing.
        if not iprop._proxies:
            iprop._proxies = WeakKeyDictionary()

        # First get all the instance attr of the IProperty to preserve the
        # special behaviours imparted by the HasIProps object.
        aux = iprop.__dict__.copy()
        aux.update(attrs)
        self.patch(aux)

        iprop._proxies[instance] = self

    def patch(self, attrs):
        """Update the proxy with new values.

        Parameters
        ----------
        attrs : dict
            New values to give to the proxy attributes.

        """
        for k, v in attrs.items():
            # Make sure the instance method are correctly redirected to the
            # proxy and the functions are bound to the proxy.
            if isinstance(v, MethodType):
                v = MethodType(v.__func__, self)
            elif isinstance(v, FunctionType):
                v = MethodType(v, self)
            setattr(self, k, v)

    def unpatch(self, attrs):
        """Reverse the proxy behaviour to the original IProperty behaviour.

        Parameters
        ----------
        attrs : iterable
            Names of the attrs whose values should match again the one of the
            IProperty.

        """
        i_dir = self._iprop.__dict__
        for attr in attrs:
            if attr in i_dir:
                v = i_dir[attr]
                if isinstance(v, MethodType):
                    v = MethodType(v.__func__, self)
                setattr(self, attr, getattr(self._iprop, attr))
            else:
                delattr(self, attr)

    @property
    def obsolete(self):
        """Boolean indicating whether the proxy differ from the original.

        """
        ip_dict = self._iprop.__dict__
        test_meth = MethodType(lambda: None, object())
        for k, v in self.__dict__.items():
            if isinstance(v, MethodType):
                if v.__func__ != ip_dict.get(k, test_meth).__func__:
                    return False
            elif k not in ('_iprop', 'instance'):
                if k not in ip_dict or v != ip_dict[k]:
                    return False

        return True

    proxy_get = get_chain

    proxy_set = set_chain
