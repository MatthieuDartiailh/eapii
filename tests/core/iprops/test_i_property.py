# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from nose.tools import (assert_equal, assert_true, assert_raises,
                        assert_not_equal, assert_is_not)
from types import MethodType

from eapii.core.iprops.i_property import IProperty


class FalseDriver(object):

    secure_com_exceptions = ()

    def __init__(self):
        self._cache = {}

    def reopen_connection(self):
        pass

    def default_check_instr_operation(self):
        return True, None


class TestGettingChain(object):
    """
    """
    def setup(self):
        p = IProperty()

        def getter(self, obj):
            return 'Test'

        p.get = MethodType(getter, p)
        self.p = p

    def test_default_post_get(self):
        assert_equal(self.p._get(FalseDriver()), 'Test')

    def test_overriding_post_get(self):
        def post_getter(self, obj, val):
            return '<br>'+val+'<br>'

        self.p.post_get = MethodType(post_getter, self.p)
        assert_equal(self.p._get(FalseDriver()), '<br>Test<br>')

    def test_caching(self):
        p = self.p

        def getter(self, obj):
            obj.i += 1
            return obj.i

        p.get = MethodType(getter, p)

        d = FalseDriver()
        d.i = 0

        assert_equal(p._get(d), 1)
        assert_equal(p._get(d), 1)
        d._cache = {}
        assert_equal(p._get(d), 2)

    def test_secur_comm_0(self):
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
        assert_equal(self.p.call, 1)

    def test_secur_comm_2(self):
        self.p.call = 0
        self.p._secur = 1

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
        assert_equal(self.p.call, 2)


class TestSettingChain(object):
    """
    """
    def setup(self):
        p = IProperty()

        def setter(self, obj, value):
            self.val = value

        p.set = MethodType(setter, p)
        self.p = p

    def test_default_set_chain(self):
        self.p._set(FalseDriver(), 1)
        assert_equal(self.p.val, 1)

    def test_overriding_pre_set(self):
        def pre_setter(self, obj, value):
            return value/2

        self.p.pre_set = MethodType(pre_setter, self.p)
        self.p._set(FalseDriver(), 1)
        assert_equal(self.p.val, 0.5)

    def test_overriding_post_set(self):
        def pre_setter(self, obj, value):
            return value/2

        def post_setter(self, obj, value, i_value):
            self.val = (value, i_value)

        self.p.pre_set = MethodType(pre_setter, self.p)
        self.p.post_set = MethodType(post_setter, self.p)
        self.p._set(FalseDriver(), 1)
        assert_equal(self.p.val, (1, 0.5))

    def test_caching(self):
        self.p.call = 0

        def post_setter(self, obj, value, i_value):
            self.call += 1

        self.p.post_set = MethodType(post_setter, self.p)

        d = FalseDriver()
        self.p._set(d, 1)
        self.p._set(d, 1)
        assert_equal(self.p.call, 1)

    def test_secur_comm_0(self):
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
        assert_equal(self.p.call, 1)

    def test_secur_comm_2(self):
        self.p.call = 0
        self.p._secur = 1

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
        assert_equal(self.p.call, 2)


def test_cloning():
    p = IProperty(True, True)

    def aux(self, obj):
        return self
    m = MethodType(aux, p)
    p.get = m
    p.val = 1

    p2 = p.clone()
    assert_is_not(p2, p)
    assert_equal(p2.val, 1)
    assert_equal(p2.get.__func__, aux)
    assert_not_equal(p2.get(None), p.get(None))
