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
from collections import OrderedDict

from ..core.iprops.i_property import IProperty


class Register(IProperty):
    """Property handling a bit field as a mapping.

    Parameters
    ----------
    getter : unicode
        Command to retrieve the byte state.
    setter : unicode
        Command to set the byte state.
    names : iterable or dict
        Names to associate to each bit fields from 0 to 7. When using an
        iterable None can be used to mark a useless bit. When using a dict
        the values are used to specify the bits to consider.
    secure_comm : int, optional
        Whether or not a failed communication should result in a new attempt
        to communicate after re-opening the communication. The value is used to
        determine how many times to retry.

    """
    def __init__(self, getter=None, setter=None, names=(), checks=None,
                 secure_comm=0):
        super(Register, self).__init__(getter, setter, secure_comm, checks)

        if isinstance(names, dict):
            aux = list(range(8))
            for n, i in names.items():
                aux[i] = n
            names = aux

        else:
            names = list(names)
            if len(names) != 8:
                raise ValueError('Register necessitates 8 names')

            # Makes sure every key is unique by using the bit index if None is
            # found
            for i, n in enumerate(names[:]):
                if n is None:
                    names[i] = i

        self.names = tuple(names)
        self.creation_kwargs['names'] = names

    def post_get(self, instance, value):
        """Convert the instrument into a dict.

        """
        val = int(value)
        bit_conversion = lambda x, i: bool(x & (1 << i))
        return OrderedDict((n, bit_conversion(val, i))
                           for i, n in enumerate(self.names)
                           if n is not None)

    def pre_set(self, instance, value):
        """Convert a dict into a byte value.

        """
        byte = sum((2**self.names.index(k) for k in value if value[k]))
        return byte
