# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Module dedicated to testing IProperty behaviour.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from types import MethodType
from threading import RLock
from pytest import raises

from eapii.core.iprops.i_property import IProperty


class FalseDriver(object):

    secure_com_exceptions = ()

    def __init__(self):
        self._cache = {}
        self.lock = RLock()
        self._caching_permissions = set()

    def reopen_connection(self):
        pass

    def default_check_instr_operation(self, iprop):
        return True, None

    def clear_cache(self, properties):
        for p in properties:
            del self._cache[p]


class TestGettingChain(object):

    def setup(self):
        p = IProperty()
        p.name = 'test'

        def getter(self, obj):
            return 'Test'

        p.get = MethodType(getter, p)
        self.p = p

    def test_default_post_get(self):
        assert self.p._get(FalseDriver()) == 'Test'

    def test_overriding_post_get(self):
        def post_getter(self, obj, val):
            return '<br>'+val+'<br>'

        self.p.post_get = MethodType(post_getter, self.p)
        assert self.p._get(FalseDriver()) == '<br>Test<br>'

    def test_overriding_pre_get(self):
        def pre_getter(self, obj):
            assert False

        self.p.pre_get = MethodType(pre_getter, self.p)
        with raises(AssertionError):
            self.p._get(FalseDriver())

    def test_caching(self):
        p = self.p

        def getter(self, obj):
            obj.i += 1
            return obj.i

        p.get = MethodType(getter, p)

        d = FalseDriver()
        d.i = 0

        assert p._get(d) == 1
        assert p._get(d) == 2
        d._caching_permissions = set(['test'])
        assert p._get(d) == 3
        assert p._get(d) == 3

    def test_deleter(self):
        p = self.p

        def getter(self, obj):
            obj.i += 1
            return obj.i

        p.get = MethodType(getter, p)

        d = FalseDriver()
        d._caching_permissions = set(['test'])
        d.i = 0

        assert p._get(d) == 1
        assert p._get(d) == 1
        p._del(d)
        assert p._get(d) == 2

    def test_secur_comm_1(self):
        self.p.call = 0

        def getter(self, obj):
            self.call += 1
            raise ValueError()

        self.p.get = MethodType(getter, self.p)

        d = FalseDriver()
        d.secure_com_exceptions = (ValueError)
        try:
            self.p._get(d)
        except ValueError:
            pass
        assert self.p.call == 1

    def test_secur_comm_2(self):
        self.p.call = 0
        self.p._secur = 5

        def getter(self, obj):
            self.call += 1
            raise ValueError()

        self.p.get = MethodType(getter, self.p)

        d = FalseDriver()
        d.secure_com_exceptions = (ValueError)
        try:
            self.p._get(d)
        except ValueError:
            pass
        assert self.p.call == 6

    def test_secur_comm_3(self):
        self.p.call = 0
        self.p._secur = 10

        def getter(self, obj):
            self.call += 1
            if self.call == 2:
                return
            raise ValueError()

        self.p.get = MethodType(getter, self.p)

        d = FalseDriver()
        d.secure_com_exceptions = (ValueError)
        try:
            self.p._get(d)
        except ValueError:
            pass
        assert self.p.call == 2


class TestSettingChain(object):
    """
    """
    def setup(self):
        p = IProperty()
        p.name = 'test'

        def setter(self, obj, value):
            self.val = value

        p.set = MethodType(setter, p)
        self.p = p

    def test_default_set_chain(self):
        self.p._set(FalseDriver(), 1)
        assert self.p.val == 1

    def test_overriding_pre_set(self):
        def pre_setter(self, obj, value):
            return value/2

        self.p.pre_set = MethodType(pre_setter, self.p)
        self.p._set(FalseDriver(), 1)
        assert self.p.val == 0.5

    def test_overriding_post_set(self):
        def pre_setter(self, obj, value):
            return value/2

        def post_setter(self, obj, value, i_value):
            self.val = (value, i_value)

        self.p.pre_set = MethodType(pre_setter, self.p)
        self.p.post_set = MethodType(post_setter, self.p)
        self.p._set(FalseDriver(), 1)
        assert self.p.val == (1, 0.5)

    def test_caching(self):
        self.p.call = 0

        def post_setter(self, obj, value, i_value):
            self.call += 1

        self.p.post_set = MethodType(post_setter, self.p)

        d = FalseDriver()
        self.p._set(d, 1)
        self.p._set(d, 1)
        assert self.p.call == 2
        d._caching_permissions = set(['test'])

        self.p._set(d, 1)
        self.p._set(d, 1)
        assert self.p.call == 3

    def test_secur_comm_1(self):
        self.p.call = 0

        def setter(self, obj, value):
            self.call += 1
            raise ValueError()

        self.p.set = MethodType(setter, self.p)

        d = FalseDriver()
        d.secure_com_exceptions = (ValueError)
        try:
            self.p._set(d, 1)
        except ValueError:
            pass
        assert self.p.call == 1

    def test_secur_comm_2(self):
        self.p.call = 0
        self.p._secur = 5

        def setter(self, obj, value):
            self.call += 1
            raise ValueError()

        self.p.set = MethodType(setter, self.p)

        d = FalseDriver()
        d.secure_com_exceptions = (ValueError)
        try:
            self.p._set(d, 1)
        except ValueError:
            pass
        assert self.p.call == 6

    def test_secur_comm_3(self):
        self.p.call = 0
        self.p._secur = 10

        def setter(self, obj, value):
            self.call += 1
            if self.call == 2:
                return
            raise ValueError()

        self.p.set = MethodType(setter, self.p)

        d = FalseDriver()
        d.secure_com_exceptions = (ValueError)
        try:
            self.p._set(d, 1)
        except ValueError:
            pass
        assert self.p.call == 2


def test_cloning():
    p = IProperty(True, True)

    def aux(self, obj):
        return self
    m = MethodType(aux, p)
    p.get = m
    p.val = 1
    p.__doc__ = 'test'

    p2 = p.clone()
    assert p2 is not p
    assert p2.val == 1
    assert p2.get.__func__ == aux
    assert p2.get(None) != p.get(None)
    assert p2.__doc__ == p.__doc__


def test_checkers():

    class Tester(FalseDriver):
        t1 = True
        t2 = False

    p = IProperty(True, checks='{t1} is True; {t2} == False')
    p.name = 'test'
    p.get = MethodType(lambda s, o: None, p)
    p.set = MethodType(lambda s, o, v: v, p)
    t = Tester()

    assert hasattr(p, 'get_check')
    assert p.pre_get is p.get_check
    assert hasattr(p, 'set_check')
    assert p.pre_set is p.set_check

    p._get(t)
    p._set(t, 1)
    t.t2 = True

    with raises(AssertionError):
        p._get(t)
    try:
        p._get(t)
    except AssertionError as e:
        m = 'Getting test assertion t2 == False failed, values are : t2=True'
        assert e.message == m

    with raises(AssertionError):
        p._set(t, 1)
    try:
        p._set(t, 1)
    except AssertionError as e:
        m = 'Setting test assertion t2 == False failed, values are : t2=True'
        assert e.message == m


def test_get_check():

    class Tester(FalseDriver):
        t1 = True
        t2 = False

    p = IProperty(True, checks=('{t1} is True; {t2} == False', None))
    p.name = 'test'
    p.get = MethodType(lambda s, o: None, p)
    p.set = MethodType(lambda s, o, v: v, p)
    t = Tester()

    assert hasattr(p, 'get_check')
    assert not hasattr(p, 'set_check')

    p._get(t)
    t.t2 = True
    with raises(AssertionError):
        p._get(t)
    try:
        p._get(t)
    except AssertionError as e:
        m = 'Getting test assertion t2 == False failed, values are : t2=True'
        assert e.message == m


def test_set_check():

    class Tester(FalseDriver):
        t1 = True
        t2 = False

    p = IProperty(True, checks=(None, '{t1} is True; {t2} == False'))
    p.name = 'test'
    p.get = MethodType(lambda s, o: None, p)
    p.set = MethodType(lambda s, o, v: v, p)
    t = Tester()

    assert not hasattr(p, 'get_check')
    assert hasattr(p, 'set_check')

    p._get(t)
    p._set(t, 1)
    t.t2 = True

    with raises(AssertionError):
        p._set(t, 1)
    try:
        p._set(t, 1)
    except AssertionError as e:
        m = 'Setting test assertion t2 == False failed, values are : t2=True'
        assert e.message == m


class TestWrapWithChecker():

    def setup(self):
        class Tester(FalseDriver):
            def __init__(self):
                super(Tester, self).__init__()
                self.t1 = True
                self.t2 = False
        self.t = Tester()

    def test_wrapping_get_checker_exists(self):
        p = IProperty(True, checks='{t1} is True; {t2} == False')

        # Wrapping function
        f = lambda s, o: 'test'
        p._wrap_with_checker(f)
        assert p.pre_get.__func__ is not f
        assert p.pre_get(self.t) == 'test'

        # Wrapping method
        f = MethodType(lambda s, o: 'test', p)
        p._wrap_with_checker(f)
        assert p.pre_get is not f
        assert p.pre_get(self.t) == 'test'

    def test_wrapping_get_no_checker(self):
        p = IProperty(True, checks=(None, '{t1} is True; {t2} == False'))

        # Wrapping function
        f = lambda s, o: 'test'
        p._wrap_with_checker(f)
        assert p.pre_get.__func__ is f

        # Wrapping method
        f = MethodType(lambda s, o: 'test', p)
        p._wrap_with_checker(f)
        assert p.pre_get is f

    def test_wrapping_set_checker_exists(self):
        p = IProperty(True, checks='{t1} is True; {t2} == False')

        # Wrapping function
        f = lambda s, o, v: 'test'
        p._wrap_with_checker(f, 'pre_set')
        assert p.pre_set.__func__ is not f
        assert p.pre_set(self.t, None) == 'test'

        # Wrapping method
        f = MethodType(lambda s, o, v: 'test', p)
        p._wrap_with_checker(f, 'pre_set')
        assert p.pre_set is not f
        assert p.pre_set(self.t, None) == 'test'

    def test_wrapping_set_no_checker(self):
        p = IProperty(True, checks=('{t1} is True; {t2} == False', None))

        # Wrapping function
        f = lambda s, o, v: 'test'
        p._wrap_with_checker(f, 'pre_set')
        assert p.pre_set.__func__ is f

        # Wrapping method
        f = MethodType(lambda s, o, v: 'test', p)
        p._wrap_with_checker(f, 'pre_set')
        assert p.pre_set is f

    def test_wrapping_exception(self):
        p = IProperty(True, checks=('{t1} is True; {t2} == False', None))

        # Wrapping function
        f = lambda s, o, v: 'test'
        with raises(ValueError):
            p._wrap_with_checker(f, None)
