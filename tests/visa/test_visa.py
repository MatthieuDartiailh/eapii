# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Module dedicated to testing the visa utilities functions.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from pytest import raises, yield_fixture

from pyvisa.highlevel import ResourceManager
from eapii.visa.visa import (get_visa_resource_manager,
                             set_visa_resource_manager)
from eapii.visa import visa


@yield_fixture
def cleanup():
    visa.RESOURCE_MANAGER = None
    yield
    visa.RESOURCE_MANAGER = None


def test_get_rm(cleanup):
    rm = get_visa_resource_manager('@sim')
    assert rm is visa.RESOURCE_MANAGER


def test_set_rm(cleanup):
    rm = ResourceManager('@sim')
    set_visa_resource_manager(rm)
    assert rm is get_visa_resource_manager()


def test_reset_rm(cleanup):
    get_visa_resource_manager('@sim')
    with raises(ValueError):
        rm = ResourceManager('@sim')
        set_visa_resource_manager(rm)
