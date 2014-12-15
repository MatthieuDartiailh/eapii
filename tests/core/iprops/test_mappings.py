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

from eapii.core.iprops.mappings import Mapping, Bool


def test_mapping():
    m = Mapping(mapping={'On': 1, 'Off': 2})
    assert m.post_get(None, 1) == 'On'
    assert m.post_get(None, 2) == 'Off'

    assert m.pre_set(None, 'On') == 1
    assert m.pre_set(None, 'Off') == 2


def test_bool():
    b = Bool(mapping={True: 1, False: 2},
             aliases={True: ['On', 'on', 'ON'], False: ['Off', 'off', 'OFF']})
    assert b.pre_set(None, 'ON') == 1
    assert b.pre_set(None, 'off') == 2
