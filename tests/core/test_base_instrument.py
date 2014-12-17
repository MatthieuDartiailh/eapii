# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Module dedicated to testing BaseInstrument behaviour.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from nose.tools import raises, assert_true, assert_false, assert_is

from eapii.core.base_instrument import BaseInstrument


def test_binstr_multiple_creation():
    a = BaseInstrument({'a': 1})
    assert_true(hasattr(a, 'owner'))
    assert_true(hasattr(a, 'lock'))
    assert_true(a.newly_created)
    b = BaseInstrument({'a': 1})
    assert_is(a, b)
    assert_false(b.newly_created)


@raises(NotImplementedError)
def test_binstr_open():
    BaseInstrument({'a': 1}).open_connection()


@raises(NotImplementedError)
def test_binstr_close():
    BaseInstrument({'a': 1}).close_connection()


def test_binstr_check():
    assert not BaseInstrument({'a': 1}).check_connection()


@raises(NotImplementedError)
def test_binstr_connected():
    BaseInstrument({'a': 1}).connected
