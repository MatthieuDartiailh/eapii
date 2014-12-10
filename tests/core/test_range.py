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
from pytest import raises

from eapii.core.range import IntRangeValidator, FloatRangeValidator


def teardown_module():
    from eapii.core import unit
    unit.ureg = None


class TestIntRangeValidator(object):

    def test_validate_larger(self):
        iv = IntRangeValidator(1)

        assert iv.validate(2)
        assert iv.validate(1)
        assert not iv.validate(0)

    def test_validate_smaller(self):
        iv = IntRangeValidator(max=1)

        assert iv.validate(0)
        assert iv.validate(1)
        assert not iv.validate(2)

    def test_validate_range(self):
        iv = IntRangeValidator(1, 4)

        assert iv.validate(2)
        assert iv.validate(1)
        assert iv.validate(4)
        assert not iv.validate(0)
        assert not iv.validate(5)

    def test_validate_larger_and_step(self):
        iv = IntRangeValidator(1, step=2)

        assert iv.validate(3)
        assert iv.validate(1)
        assert not iv.validate(0)
        assert not iv.validate(2)

    def test_validate_smaller_and_step(self):
        iv = IntRangeValidator(max=5, step=2)

        assert iv.validate(3)
        assert iv.validate(5)
        assert not iv.validate(6)
        assert not iv.validate(4)

    def test_validate_range_and_step(self):
        iv = IntRangeValidator(1, 4, 2)

        assert iv.validate(3)
        assert iv.validate(1)
        assert not iv.validate(6)
        assert not iv.validate(4)
        assert not iv.validate(0)

    def test_init_checks(self):
        with raises(ValueError):
            IntRangeValidator(step=1)
        with raises(TypeError):
            IntRangeValidator(1.0)
        with raises(TypeError):
            IntRangeValidator(max=1.0)
        with raises(TypeError):
            IntRangeValidator(1, step=1.0)


class TestFloatRangeValidator(object):

    def test_validate_larger(self):
        iv = FloatRangeValidator(0.1)

        assert iv.validate(2.1)
        assert iv.validate(0.1)
        assert not iv.validate(0.05)

    def test_validate_smaller(self):
        iv = FloatRangeValidator(max=1.1)

        assert iv.validate(1.1)
        assert iv.validate(1)
        assert not iv.validate(2.3)

    def test_validate_range(self):
        iv = FloatRangeValidator(1.5, 4.2)

        assert iv.validate(1.5)
        assert iv.validate(4.2)
        assert iv.validate(2.3)
        assert not iv.validate(1.499999)
        assert not iv.validate(4.200002)

    def test_validate_larger_and_step(self):
        iv = FloatRangeValidator(1.0, step=0.1)

        assert iv.validate(1.0)
        assert iv.validate(1.1)
        assert iv.validate(10000000.9)
        assert not iv.validate(0.999999)
        assert not iv.validate(1.05)

    def test_validate_smaller_and_step(self):
        iv = FloatRangeValidator(max=5.1, step=0.0001)

        assert iv.validate(5.1)
        assert iv.validate(4.0002)
        assert not iv.validate(6)
        assert not iv.validate(5.00001)

    def test_validate_range_and_step(self):
        iv = FloatRangeValidator(1.1, 4.2, 0.02)

        assert iv.validate(1.1)
        assert iv.validate(4.2)
        assert iv.validate(1.12)
        assert not iv.validate(6)
        assert not iv.validate(4.01)
        assert not iv.validate(0)

    def test_init_checks(self):
        with raises(ValueError):
            FloatRangeValidator(step=1)
        with raises(TypeError):
            FloatRangeValidator(1)
        with raises(TypeError):
            FloatRangeValidator(max=1)
        with raises(TypeError):
            FloatRangeValidator(1.0, step=1)
