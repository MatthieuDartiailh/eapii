# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Standards errors used in Eapii

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)


class InstrError(Exception):
    """Generic error refereing to instrument.

    """
    pass


class InstrIOError(InstrError):
    """Generic errors for communication errors.

    """
    pass
