# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Module dedicated to testing the mappings iproperties.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from pytest import raises

from eapii.core.iprops.scalars import Unicode, Int, Float
from eapii.core.range import IntRangeValidator, FloatRangeValidator
from eapii.core.unit import get_unit_registry
from ..testing_tools import Parent


def test_unicode():
    u = Unicode(setter=True, values=['On', 'Off'])
    assert u.pre_set(None, 'On') == 'On'
    with raises(ValueError):
        u.pre_set(None, 'TEST')
    assert isinstance(u.post_get(None, 1), type(''))


class TestInt(object):

    def test_post_get(self):
        i = Int()
        assert i.post_get(None, '11') == 11

    def test_with_values(self):
        i = Int(setter=True, values=(1, 2, 3))
        assert i.pre_set(None, 2) == 2
        with raises(ValueError):
            i.pre_set(None, 5)
        del i.pre_set
        assert i.pre_set(None, 5)

    def test_with_static_range(self):
        i = Int(setter=True, values=(1,), range=IntRangeValidator(2, step=2))
        with raises(ValueError):
            i.pre_set(None, 1)
        assert i.pre_set(None, 4)
        with raises(ValueError):
            i.pre_set(None, 3)

    def test_with_dynamic_range(self):

        class RangeHolder(Parent):

            n = 0

            def _range_test(self):
                self.n += 1
                return IntRangeValidator(self.n)
        o = RangeHolder()
        i = Int(setter=True, range='test')
        assert i.pre_set(o, 1)
        with raises(ValueError):
            i.pre_set(o, 0)
        o.discard_range('test')
        with raises(ValueError):
            i.pre_set(o, 1)


class TestFloat(object):

    def test_post_get(self):
        f = Float()
        assert f.post_get(None, '0.1') == 0.1

    def test_post_get_with_unit(self):
        f = Float(unit='V')
        assert hasattr(f.post_get(None, 0.1), 'magnitude')
        assert f.post_get(None, 0.1).to('mV').magnitude == 100.

    def test_set_with_static_range(self):
        f = Float(setter=True, range=FloatRangeValidator(0.0))
        assert f.pre_set(None, 0.1) == 0.1
        with raises(ValueError):
            f.pre_set(None, -1.0)

    def test_set_with_dynamic_range(self):

        class RangeHolder(Parent):

            n = 0.1

            def _range_test(self):
                self.n += .1
                return FloatRangeValidator(0.0, step=self.n)

        o = RangeHolder()
        f = Float(setter=True, range='test')
        assert f.pre_set(o, .2)
        with raises(ValueError):
            f.pre_set(o, -0.5)
        o.discard_range('test')
        with raises(ValueError):
            f.pre_set(o, 0.2)

    def test_set_with_unit(self):
        f = Float(setter=True, unit='mV')
        u = get_unit_registry()
        assert f.pre_set(None, u.parse_expression('10 V')) == 10000.

    def test_with_static_range_and_units(self):
        f = Float(setter=True,
                  range=FloatRangeValidator(-1.0, 1.0, 0.01, unit='V'))
        u = get_unit_registry()
        assert f.pre_set(None, 0.1) == 0.1
        with raises(ValueError):
            f.pre_set(None, -2.0)
        assert f.pre_set(None, u.parse_expression('10 mV')) == 10.
        with raises(ValueError):
            f.pre_set(None, u.parse_expression('0.1 mV'))

    def test_with_dynamic_range_and_units(self):

        class RangeHolder(Parent):

            n = 0.0

            def _range_test(self):
                self.n += 100
                return FloatRangeValidator(-1000., 1000., step=self.n,
                                           unit='mV')

        o = RangeHolder()
        f = Float(setter=True, range='test', unit='V')
        assert f.pre_set(o, .1) == 0.1
        with raises(ValueError):
            f.pre_set(o, -5)
        o.discard_range('test')
        with raises(ValueError):
            f.pre_set(o, 0.1)

        u = get_unit_registry()
        assert f.pre_set(o, u.parse_expression('200 mV')) == 0.2
        with raises(ValueError):
            f.pre_set(o, u.parse_expression('100 mV'))
