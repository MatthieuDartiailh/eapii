# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Module dedicated to testing the unit utility functions.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from pytest import raises, yield_fixture
from pint import UnitRegistry

from eapii.core import unit
from eapii.core.unit import set_ureg, get_ureg


@yield_fixture
def teardown():
    yield
    unit.ureg = None


def test_set_ureg(teardown):
    ureg = UnitRegistry()
    set_ureg(ureg)

    assert get_ureg() is ureg


def test_reset_ureg(teardown):
    ureg = UnitRegistry()
    set_ureg(ureg)
    with raises(ValueError):
        set_ureg(ureg)
