# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Module dedicated to testing SubSystem behaviour.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from nose.tools import assert_equal, assert_is
from threading import RLock

from eapii.core.subsystem import SubSystem
from .testing_tools import Parent


class SSParent(Parent):

    ss = SubSystem()


def test_ss_d_get():

    a = SSParent()
    a.ss.default_get_iproperty('Test', 1, a=2)
    assert_equal(a.d_get_called, 1)
    assert_equal(a.d_get_cmd, 'Test')
    assert_equal(a.d_get_args, (1,))
    assert_equal(a.d_get_kwargs, {'a': 2})


def test_ss_d_set():
    a = SSParent()
    a.ss.default_set_iproperty('Test', 1, a=2)
    assert_equal(a.d_set_called, 1)
    assert_equal(a.d_set_cmd, 'Test')
    assert_equal(a.d_set_args, (1,))
    assert_equal(a.d_set_kwargs, {'a': 2})


def test_ss_d_check():
    a = SSParent()
    a.ss.default_check_instr_operation()
    assert_equal(a.d_check_instr, 1)


def test_ss_lock():
    a = SSParent()
    assert_is(a.ss.lock, a.lock)


def test_ss_reop():
    a = SSParent()
    a.ss.reopen_connection()
    assert_equal(a.ropen_called, 1)
