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
from nose.tools import (assert_equal, assert_true, assert_raises,
                        assert_is_instance, assert_false, assert_is,
                        assert_is_not)

from eapii.core.has_i_props import HasIProps
from eapii.core.subsystem import SubSystem
from eapii.core.channel import Channel
from eapii.core.iprops.i_property import IProperty


class HasIPropsTester(HasIProps):
    """
    """
    def reopen_connection(self):
        pass

    def default_check_instr_operation(self):
        return True, None


def test_overriding_get():

    class NoOverrideGet(HasIPropsTester):
        test = IProperty(getter=True)

    assert_raises(NotImplementedError,
                  lambda: getattr(NoOverrideGet(), 'test'))

    class OverrideGet(HasIPropsTester):
        test = IProperty(getter=True)

        def _get_test(self, iprop):
            return 'This is a test'

    assert_equal(OverrideGet().test, 'This is a test')


def test_overriding_post_get():

    class OverridePostGet(HasIPropsTester):
        test = IProperty(getter=True)

        def _get_test(self, iprop):
            return 'this is a test'

        def _post_get_test(self, iprop, val):
            return '<br>'+val+'<br>'

    assert_equal(OverridePostGet().test, '<br>this is a test<br>')


def test_overriding_set():

    class NoOverrideSet(HasIPropsTester):
        test = IProperty(setter=True)

    assert_raises(NotImplementedError,
                  lambda: setattr(NoOverrideSet(), 'test', 1))

    class OverrideSet(HasIPropsTester):
        test = IProperty(setter=True)

        def _set_test(self, iprop, value):
            self.val = value

    o = OverrideSet()
    o.test = 1
    assert_equal(o.val, 1)


def test_overriding_pre_set():

    class OverridePreSet(HasIPropsTester):
        test = IProperty(setter=True)

        def _set_test(self, iprop, value):
            self.val = value

        def _pre_set_test(self, iprop, value):
            return value/2

    o = OverridePreSet()
    o.test = 1
    assert_equal(o.val, 0.5)


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
    assert_equal(o.val, (1, 0.5))


def test_caching_permissions():

    class Cache(HasIProps):
        caching_permissions = {'b': True, 'c': False}

    a = Cache(caching_permissions={'a': True})
    assert_equal(a._caching_permissions, set(['a', 'b']))
    assert_equal(Cache.caching_permissions, {'b': True, 'c': False})

    b = Cache(caching_allowed=False, caching_permissions={'a': True})
    assert_equal(b._caching_permissions, set())


def test_subsystem_declaration():

    class DeclareSubsystem(HasIPropsTester):

        sub_test = SubSystem()

    d = DeclareSubsystem(caching_permissions={'sub_test': {'aa': True}})
    assert_true(d.__subsystems__)
    assert_is_instance(d.sub_test, SubSystem)
    assert_true(d.sub_test._caching_permissions)

    d = DeclareSubsystem(caching_allowed=False,
                         caching_permissions={'sub_test': {'aa': True}})
    assert_false(d.sub_test._caching_permissions)

    d = DeclareSubsystem(caching_permissions={'sub_test': {}})
    assert_false(d.sub_test._caching_permissions)


def test_channel_declaration():

    class Dummy(Channel):
        pass

    class DeclareChannel(HasIPropsTester):

        ch = Dummy()

    d = DeclareChannel(caching_permissions={'ch': {'aa': True}})
    assert_true(d.__channels__)
    assert_true(hasattr(d, 'get_ch'))
    channel = d.get_ch(1)
    assert_is_instance(channel, Dummy)
    assert_true(channel._caching_permissions)
    assert_is(d.get_ch(1), channel)

    d = DeclareChannel(caching_allowed=False,
                       caching_permissions={'ch': {'aa': True}})
    assert_false(d.get_ch(1)._caching_permissions)

    d = DeclareChannel(caching_permissions={'ch': {}})
    assert_false(d.get_ch(1)._caching_permissions)


def test_clone_if_needed():

    prop = IProperty(getter=True)

    class Overriding(HasIPropsTester):
        test = prop

        def _get_test(self, iprop):
            return 1

    assert_is(Overriding.test, prop)

    class OverridingParent(Overriding):

        def _get_test(self):
            return 2

    assert_is_not(OverridingParent.test, prop)


def test_get_range():

    pass


def test_discard_range():
    pass


class TestHasIPropsCache(object):

    def setup(self):

        class CacheSS(SubSystem):
            caching_permissions = {'test': True}
            test = IProperty()

        class CacheChannel(Channel):
            caching_permissions = {'aux': True}
            aux = IProperty()

        class CacheTest(HasIPropsTester):
            caching_permissions = {'test1': True, 'test2': True}
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
        assert_equal(self.a._cache, {})
        assert_equal(self.ss._cache, {})
        assert_equal(self.ch1._cache, {})
        assert_equal(self.ch2._cache, {})

    def test_clear_save_ss(self):

        self.a.clear_cache(False)
        assert_equal(self.a._cache, {})
        assert_equal(self.ss._cache, {'test': 1})
        assert_equal(self.ch1._cache, {})
        assert_equal(self.ch2._cache, {})

    def test_clear_save_ch(self):

        self.a.clear_cache(channels=False)
        assert_equal(self.a._cache, {})
        assert_equal(self.ss._cache, {})
        assert_equal(self.ch1._cache, {'aux': 1})
        assert_equal(self.ch2._cache, {'aux': 2})

    def test_clear_by_prop(self):

        self.a.clear_cache(properties=['test1', 'ch.aux', 'ss.test'])
        assert_equal(self.a._cache, {'test2': 2})
        assert_equal(self.ss._cache, {})
        assert_equal(self.ch1._cache, {})
        assert_equal(self.ch2._cache, {})

    def test_check_cache_all_caches(self):
        res = self.a.check_cache()
        assert_equal(res, {'test1': 1, 'test2': 2, 'ss': {'test': 1},
                           'ch': {1: {'aux': 1}, 2: {'aux': 2}}})

    def test_check_cache_save_ss(self):
        res = self.a.check_cache(False)
        assert_equal(res, {'test1': 1, 'test2': 2,
                           'ch': {1: {'aux': 1}, 2: {'aux': 2}}})

    def test_check_cache_save_ch(self):
        res = self.a.check_cache(channels=False)
        assert_equal(res, {'test1': 1, 'test2': 2, 'ss': {'test': 1}})

    def test_check_cache_prop(self):
        res = self.a.check_cache(properties=['test1', 'ss.test', 'ch.aux'])
        assert_equal(res, {'test1': 1, 'ss': {'test': 1},
                           'ch': {1: {'aux': 1}, 2: {'aux': 2}}})


def test_def_check():
    assert_raises(NotImplementedError,
                  lambda: HasIProps().default_check_instr_operation())
