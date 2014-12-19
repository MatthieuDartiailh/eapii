# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Module dedicated to testing HasIProps behaviour.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from threading import RLock
from pytest import raises

from eapii.core.has_i_props import HasIProps, set_iprop_paras
from eapii.core.subsystem import SubSystem
from eapii.core.channel import Channel
from eapii.core.iprops.i_property import IProperty


class HasIPropsTester(HasIProps):
    """
    """
    def __init__(self, caching_allowed=True, caching_permissions={}):
        super(HasIPropsTester, self).__init__(caching_allowed,
                                              caching_permissions)
        self.lock = RLock()

    def reopen_connection(self):
        pass

    def default_check_instr_operation(self, iprop):
        return True, None


def test_documenting_i_prop():

    class DocTester(HasIPropsTester):

        #: This is the docstring for
        #: the IProperty test.
        test = IProperty()

    assert DocTester.test.__doc__ ==\
        'This is the docstring for the IProperty test.'


def test_overriding_get():

    class NoOverrideGet(HasIPropsTester):
        test = IProperty(getter=True)

    with raises(NotImplementedError):
        NoOverrideGet().test

    class OverrideGet(HasIPropsTester):
        test = IProperty(getter=True)

        def _get_test(self, iprop):
            return 'This is a test'

    assert OverrideGet().test == 'This is a test'


def test_overriding_pre_get():

    class OverridePreGet(HasIPropsTester):
        test = IProperty(getter=True)

        def _get_test(self, iprop):
            return 'this is a test'

        def _pre_get_test(self, iprop):
            assert False

    with raises(AssertionError):
        OverridePreGet().test


def test_overriding_post_get():

    class OverridePostGet(HasIPropsTester):
        test = IProperty(getter=True)

        def _get_test(self, iprop):
            return 'this is a test'

        def _post_get_test(self, iprop, val):
            return '<br>'+val+'<br>'

    assert OverridePostGet().test == '<br>this is a test<br>'


def test_overriding_set():

    class NoOverrideSet(HasIPropsTester):
        test = IProperty(setter=True)

    with raises(NotImplementedError):
        NoOverrideSet().test = 1

    class OverrideSet(HasIPropsTester):
        test = IProperty(setter=True)

        def _set_test(self, iprop, value):
            self.val = value

    o = OverrideSet()
    o.test = 1
    assert o.val == 1


def test_overriding_pre_set():

    class OverridePreSet(HasIPropsTester):
        test = IProperty(setter=True)

        def _set_test(self, iprop, value):
            self.val = value

        def _pre_set_test(self, iprop, value):
            return value/2

    o = OverridePreSet()
    o.test = 1
    assert o.val == 0.5


def test_overriding_post_set():

    class OverridePreSet(HasIPropsTester):
        test = IProperty(setter=True)

        def _set_test(self, iprop, value):
            self.val = value

        def _pre_set_test(self, iprop, value):
            return value/2

        def _post_set_test(self, iprop, val, i_val):
            self.val = (val, i_val)

    o = OverridePreSet()
    o.test = 1
    assert o.val == (1, 0.5)


def test_caching_permissions():

    class Cache(HasIProps):
        caching_permissions = ('b',)

    a = Cache(caching_permissions={'a': True})
    assert a._caching_permissions == set(['a', 'b'])
    assert Cache.caching_permissions == ('b',)

    b = Cache(caching_allowed=False, caching_permissions={'a': True})
    assert b._caching_permissions == set()


def test_subsystem_declaration():

    class DeclareSubsystem(HasIPropsTester):

        sub_test = SubSystem()

    d = DeclareSubsystem(caching_permissions={'sub_test': {'aa': True}})
    assert d.__subsystems__
    assert isinstance(d.sub_test, SubSystem)
    assert d.sub_test._caching_permissions

    d = DeclareSubsystem(caching_allowed=False,
                         caching_permissions={'sub_test': {'aa': True}})
    assert not d.sub_test._caching_permissions

    d = DeclareSubsystem(caching_permissions={'sub_test': {}})
    assert not d.sub_test._caching_permissions


def test_channel_declaration():

    class Dummy(Channel):
        pass

    class DeclareChannel(HasIPropsTester):

        ch = Dummy()

    d = DeclareChannel(caching_permissions={'ch': {'aa': True}})
    assert d.__channels__
    assert hasattr(d, 'get_ch')
    channel = d.get_ch(1)
    assert isinstance(channel, Dummy)
    assert channel._caching_permissions
    assert d.get_ch(1) is channel

    d = DeclareChannel(caching_allowed=False,
                       caching_permissions={'ch': {'aa': True}})
    assert not d.get_ch(1)._caching_permissions

    d = DeclareChannel(caching_permissions={'ch': {}})
    assert not d.get_ch(1)._caching_permissions


def test_clone_if_needed():

    prop = IProperty(getter=True)

    class Overriding(HasIPropsTester):
        test = prop

        def _get_test(self, iprop):
            return 1

    assert Overriding.test is prop

    class OverridingParent(Overriding):

        def _get_test(self):
            return 2

    assert OverridingParent.test is not prop


def test_range():

    class RangeDecl(HasIPropsTester):

        def _range_test(self):
            return object()

    assert RangeDecl.__ranges__ == set(['test'])
    decl = RangeDecl()
    r = decl.get_range('test')
    assert decl.get_range('test') is r
    decl.discard_range('test')
    assert decl.get_range('test') is not r


def test_def_check():
    with raises(NotImplementedError):
        HasIProps().default_check_instr_operation(None, None, None)


class TestHasIPropsCache(object):

    def setup(self):

        class CacheSS(SubSystem):
            caching_permissions = ('test',)
            test = IProperty()

        class CacheChannel(Channel):
            caching_permissions = ('aux',)
            aux = IProperty()

        class CacheTest(HasIPropsTester):
            caching_permissions = ('test1', 'test2')
            test1 = IProperty()
            test2 = IProperty()

            ss = CacheSS()
            ch = CacheChannel()

        self.a = CacheTest()
        self.ss = self.a.ss
        self.ch1 = self.a.get_ch(1)
        self.ch2 = self.a.get_ch(2)

        self.a._cache = {'test1': 1, 'test2': 2}
        self.ss._cache = {'test': 1}
        self.ch1._cache = {'aux': 1}
        self.ch2._cache = {'aux': 2}

    def test_clear_all_caches(self):

        self.a.clear_cache()
        assert self.a._cache == {}
        assert self.ss._cache == {}
        assert self.ch1._cache == {}
        assert self.ch2._cache == {}

    def test_clear_save_ss(self):

        self.a.clear_cache(False)
        assert self.a._cache == {}
        assert self.ss._cache == {'test': 1}
        assert self.ch1._cache == {}
        assert self.ch2._cache == {}

    def test_clear_save_ch(self):

        self.a.clear_cache(channels=False)
        assert self.a._cache == {}
        assert self.ss._cache == {}
        assert self.ch1._cache == {'aux': 1}
        assert self.ch2._cache == {'aux': 2}

    def test_clear_by_prop(self):

        self.a.clear_cache(properties=['test1', 'ch.aux', 'ss.test'])
        assert self.a._cache == {'test2': 2}
        assert self.ss._cache == {}
        assert self.ch1._cache == {}
        assert self.ch2._cache == {}

    def test_check_cache_all_caches(self):
        res = self.a.check_cache()
        assert res == {'test1': 1, 'test2': 2, 'ss': {'test': 1},
                       'ch': {1: {'aux': 1}, 2: {'aux': 2}}}

    def test_check_cache_save_ss(self):
        res = self.a.check_cache(False)
        assert res == {'test1': 1, 'test2': 2,
                       'ch': {1: {'aux': 1}, 2: {'aux': 2}}}

    def test_check_cache_save_ch(self):
        res = self.a.check_cache(channels=False)
        assert res == {'test1': 1, 'test2': 2, 'ss': {'test': 1}}

    def test_check_cache_prop(self):
        res = self.a.check_cache(properties=['test1', 'ss.test', 'ch.aux'])
        assert res == {'test1': 1, 'ss': {'test': 1},
                       'ch': {1: {'aux': 1}, 2: {'aux': 2}}}


def test_customizing():

    class DecorateIP(IProperty):

        def __init__(self, getter=True, setter=True, secure_comm=0,
                     checks=None, dec='<br>'):
            super(DecorateIP, self).__init__(getter, setter)
            self.dec = dec

        def post_get(self, iprop, val):
            return self.dec+val+self.dec

    class ParentTester(HasIPropsTester):
        test = DecorateIP(getter=True, setter=True)

        def _get_test(self, iprop):
            return 'this is a test'

    class CustomizationTester(ParentTester):

        test = set_iprop_paras(dec='<it>')

    assert CustomizationTester.test is not ParentTester.test
    aux1 = ParentTester()
    aux2 = CustomizationTester()
    assert aux1.test != aux2.test
    assert aux2.test.startswith('<it>')


class TestPatching(object):

    def setup(self):
        class DecorateIP(IProperty):

            def __init__(self, *args, **kwargs):
                super(DecorateIP, self).__init__(*args, **kwargs)
                self.dec = '<br>'

            def post_get(self, iprop, val):
                return self.dec+val+self.dec

        class PatchTester(HasIPropsTester):
            test = DecorateIP(getter=True, setter=True)

            test2 = DecorateIP(getter=True, setter=True)

            def _get_test(self, iprop):
                return 'this is a test'

            def _pre_set_test2(self, iprop, value):
                return 0.5*value

            def _set_test2(self, iprop, value):
                self.val = value

        self.obj = PatchTester()
        self.obj2 = PatchTester()

    def test_patching_attr(self):

        self.obj.patch_iprop('test', dec='<it>')
        p = type(self.obj).test
        assert p in self.obj._proxied
        assert self.obj in p._proxies
        assert self.obj.test == '<it>this is a test<it>'

    def test_patching_method(self):

        self.obj.patch_iprop('test2',
                             set=lambda p, o, v: setattr(o, 'val', 2*v))
        p = type(self.obj).test2
        self.obj.test2 = 1
        assert p in self.obj._proxied
        assert self.obj in p._proxies
        # This means that pre_set was correctly preserved.
        assert self.obj.val == 1

    def test_patching_already_patched_iprop(self):
        self.obj.patch_iprop('test', dec='<it>')
        self.obj.patch_iprop('test', post_get=lambda p, o, v: '<tt>'+v)
        p = type(self.obj).test
        assert len(self.obj._proxied) == 1
        assert len(p._proxies) == 1
        assert self.obj.test == '<tt>this is a test'

    def test_unpatching_attr_proxy_kept(self):
        self.obj.patch_iprop('test', dec='<it>',
                             post_get=lambda p, o, v: '<tt>'+v+p.dec)
        self.obj.unpatch_iprop('test', 'dec')
        assert self.obj.test == '<tt>this is a test<br>'

    def test_unpatching_attr_proxy_discarded(self):
        self.obj.patch_iprop('test', dec='<it>')
        self.obj.unpatch_iprop('test', 'dec')
        p = type(self.obj).test
        assert p not in self.obj._proxied
        assert self.obj not in p._proxies
        assert self.obj.test == '<br>this is a test<br>'

    def test_unpatching_method_proxy_kept(self):
        self.obj.patch_iprop('test', dec='<it>',
                             post_get=lambda p, o, v: '<tt>'+v+p.dec)
        self.obj.unpatch_iprop('test', 'post_get')
        assert self.obj.test == '<it>this is a test<it>'

    def test_unpatching_method_proxy_discarded(self):
        self.obj.patch_iprop('test', post_get=lambda p, o, v: '<tt>'+v+p.dec)
        self.obj.unpatch_iprop('test', 'post_get')
        p = type(self.obj).test
        assert p not in self.obj._proxied
        assert self.obj not in p._proxies
        assert self.obj.test == '<br>this is a test<br>'

    def test_raising_error(self):
        with raises(KeyError):
            self.obj.unpatch_iprop('test', 'post_get')

    def test_unpatching_all(self):
        self.obj.patch_iprop('test', dec='<it>')
        self.obj.patch_iprop('test2',
                             set=lambda p, o, v: setattr(o, 'val', 2*v))
        self.obj2.patch_iprop('test', dec='<dt>')

        self.obj.test2 = 1
        assert self.obj.test == '<it>this is a test<it>'
        assert self.obj.val == 1
        assert self.obj2.test == '<dt>this is a test<dt>'

        self.obj.unpatch_all()

        self.obj.test2 = 1
        assert self.obj.test == '<br>this is a test<br>'
        assert self.obj.val == 0.5
        assert self.obj2.test == '<dt>this is a test<dt>'
