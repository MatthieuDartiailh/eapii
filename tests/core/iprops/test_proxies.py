# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Module dedicated to testing IPropertyProxy behaviour.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from types import MethodType

from eapii.core.iprops.i_property import IProperty
from eapii.core.iprops.proxies import _ProxyManager


class WeakRef(object):
    pass


def test_make_proxy():
    ip = IProperty(getter=True)
    ip.get = MethodType(lambda s, o: False, ip)

    pm = _ProxyManager()
    ip_p = pm.make_proxy(ip, WeakRef(),
                         {'get': lambda s, o: True, 'toto': 'test'})

    assert not ip.get(None)
    assert ip_p.get(None)
    assert ip_p.toto == 'test'


def test_make_proxy_cache():
    ip = IProperty(getter=True)
    ip2 = IProperty(setter=True)

    pm = _ProxyManager()
    pm.make_proxy(ip, WeakRef(), {'get': lambda s, o: True, 'toto': 'test'})
    pm.make_proxy(ip2, WeakRef(), {'set': lambda s, o, v: None})

    assert len(pm._proxy_cache) == 1


def test_unpatch():
    ip = IProperty(getter=True)
    ip.get = MethodType(lambda s, o: False, ip)

    pm = _ProxyManager()
    ip_p = pm.make_proxy(ip, WeakRef(),
                         {'get': lambda s, o: True, 'toto': 'test'})

    ip_p.unpatch(['get'])
    assert not ip_p.get(None)
    assert ip_p.toto == 'test'


def test_obsolete():
    ip = IProperty(getter=True)
    ip.get = MethodType(lambda s, o: False, ip)

    pm = _ProxyManager()
    ip_p = pm.make_proxy(ip, WeakRef(),
                         {'get': lambda s, o: True, 'toto': 'test'})
    assert not ip_p.obsolete

    ip_p.unpatch(['get'])
    assert not ip_p.obsolete

    ip_p.unpatch(['toto'])
    assert ip_p.obsolete
