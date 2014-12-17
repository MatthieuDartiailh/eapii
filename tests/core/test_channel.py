# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Module dedicated to testing Channel behaviour.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from nose.tools import assert_equal, assert_is

from eapii.core.channel import Channel
from .testing_tools import Parent


class ChParent(Parent):

    ch = Channel()


def test_ch_d_get():

    a = ChParent()
    ch = a.get_ch(1)
    ch.default_get_iproperty(None, 'Test', 1, a=2)
    assert_equal(a.d_get_called, 1)
    assert_equal(a.d_get_cmd, 'Test')
    assert_equal(a.d_get_args, (1,))
    assert_equal(a.d_get_kwargs, {'ch_id': 1, 'a': 2})


def test_ch_d_set():

    a = ChParent()
    ch = a.get_ch(1)
    ch.default_set_iproperty(None, 'Test', 1, a=2)
    assert_equal(a.d_set_called, 1)
    assert_equal(a.d_set_cmd, 'Test')
    assert_equal(a.d_set_args, (1,))
    assert_equal(a.d_set_kwargs, {'ch_id': 1, 'a': 2})


def test_ch_d_check():

    a = ChParent()
    ch = a.get_ch(1)
    ch.default_check_instr_operation(None, None, None)
    assert_equal(a.d_check_instr, 1)


def test_ch_lock():
    a = ChParent()
    ch = a.get_ch(1)
    assert_is(ch.lock, a.lock)


def test_ch_reop():
    a = ChParent()
    ch = a.get_ch(1)
    ch.reopen_connection()
    assert_equal(a.ropen_called, 1)
