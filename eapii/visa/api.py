# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Visa package API.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from .visa import get_visa_resource_manager, set_visa_resource_manager
from .visa_instrs import (BaseVisaInstrument, VisaMessageInstrument,
                          VisaRegisterInstrument)
from .standards import IEC60488
