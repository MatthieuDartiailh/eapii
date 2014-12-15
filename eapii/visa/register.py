# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" Module defining an IProperty used to deal with 8-bits binary register.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from ..core.iprops.i_property import IProperty


class Register(IProperty):
    """Property handling a bit field as a mapping.

    Parameters
    ----------
    getter : unicode
        Command to retrieve the byte state.
    setter : unicode
        Command to set the byte state.
    names : iterable
        Names to associate to each bit fields from 0 to 7. None can be used to
        mark a useless bit.
    secure_comm : int, optional
        Whether or not a failed communication should result in a new attempt
        to communicate after re-opening the communication. The value is used to
        determine how many times to retry.

    """
    def __init__(self, getter=None, setter=None, names=(), secure_comm=0):
        super(Register, self).__init__(getter, setter, secure_comm=secure_comm)
        self.names = tuple(names)
        if len(names) != 8:
            raise ValueError('Register necessitates 8 names')

    def post_get(self, instance, value):
        """Convert the instrument into a dict.

        """
        val = int(value)
        bit_conversion = lambda x, i: bool(x & (1 << i))
        return {n: bit_conversion(val, i) for i, n in enumerate(self.names)
                if n is not None}

    def pre_set(self, instance, value):
        """Convert a dict into a byte value.

        """
        byte = sum((2**self.names.index(k) for k in value if value[k]))
        return byte
