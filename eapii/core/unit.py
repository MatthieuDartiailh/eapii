# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Unit handling is done using the Pint library.

This module allows the user to specify the UnitRegistry to be used by Eapii and
exposes some useful Pint features.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import logging
from pint import UnitRegistry


UNIT_REGISTRY = None


def set_unit_registry(unit_registry):
    """Set the UnitRegistry used by Eapii.

    Given that conversion can only happen for units declared in the same
    UnitRegistry an application should only use a single registry. This method
    should be called before doing anything else in Eapii (even importing driver
    ) to avoid the creation of a default registry by Eapii.

    Parameters
    ----------
    unit_registry : UnitRegistry
        UnitRegistry to use for Eapii.

    Raises
    ------
    ValueError:
        If a unit registry has already been set.

    """
    global UNIT_REGISTRY
    if UNIT_REGISTRY:
        mess = 'The unit registry used by Eapii cannot be changed once set.'
        raise ValueError(mess)

    UNIT_REGISTRY = unit_registry


def get_unit_registry():
    """Access the UnitRegistry currently in use by Eapii.

    If no UnitRegistry has been previously declared using `set_ureg`, a new
    UnitRegistry  is created.

    """
    global UNIT_REGISTRY
    if not UNIT_REGISTRY:
        logger = logging.getLogger(__name__)
        logger.debug('Creating default UnitRegistry for Eapii')
        UNIT_REGISTRY = UnitRegistry()

    return UNIT_REGISTRY
