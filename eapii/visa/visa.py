# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" Module importing the pyvisa module components.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
import logging
from inspect import cleandoc

from pyvisa.highlevel import ResourceManager
from pyvisa.errors import VisaIOError, VisaTypeError
from pyvisa import constants


# XXXX consider supporting multiple rm with different backends
RESOURCE_MANAGER = None


def get_visa_resource_manager(backend='@ni'):
    """Access the VISA ressource manager in use by Eapii.

    """
    global RESOURCE_MANAGER
    if not RESOURCE_MANAGER:
        mess = cleandoc('''Creating default Visa resource manager for Eapii
            with backend {}.'''.format(backend))
        logging.debug(mess)
        RESOURCE_MANAGER = ResourceManager(backend)

    return RESOURCE_MANAGER


def set_visa_resource_manager(rm):
    """Set the VISA ressource manager in use by Eapii.

    This operation can only be performed once, and should be performed
    before any driver relying on the visa protocol is created.

    Parameters
    ----------
    rm : RessourceManager
        Instance to use as Eapii default resource manager.

    """
    global RESOURCE_MANAGER
    if RESOURCE_MANAGER:
        mess = 'Cannot set Eapii resource manager once one already exists.'
        raise ValueError(mess)

    RESOURCE_MANAGER = rm
