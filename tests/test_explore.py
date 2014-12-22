# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Module dedicated to testing the explore module utility functions.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from eapii.explore import list_drivers, list_driver_types


def test_list_drivers():
    assert 'YokogawaGS200' in list_drivers()


def test_list_driver_types():
    assert 'VisaMessage' in list_driver_types()
