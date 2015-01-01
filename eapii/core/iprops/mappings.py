# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" Property for values requiring a mapping between user and instrs values.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from .i_property import IProperty


class Mapping(IProperty):
    """ Property using a dict to map user input to instrument and back.

    Parameters
    ----------
    mapping : dict
        Mapping between the user values and instrument values.

    """
    def __init__(self, getter=None, setter=None, secure_comm=0, checks=None,
                 mapping={}):
        super(Mapping, self).__init__(getter, setter, secure_comm)
        self._map = mapping
        self._imap = {v: k for k, v in mapping.items()}
        self.creation_kwargs['mapping'] = mapping

        self._wrap_with_checker(self.map_value, 'pre_set')

    def post_get(self, instance, value):
        return self._imap[value]

    def map_value(self, instance, value):
        return self._map[value]


class Bool(Mapping):
    """ Boolean property.

    True/False are mapped to the mapping values, aliases can also be declared
    to accept non-boolean values.

    Parameters
    ----------
    aliases : dict, optional
        Keys should be True and False and values the list of aliases.

    """
    def __init__(self, getter=None, setter=None, secure_comm=0, checks=None,
                 mapping={}, aliases={}):
        super(Bool, self).__init__(getter, setter, secure_comm, checks,
                                   mapping)
        self._aliases = {True: True, False: False}
        if aliases:
            for k in aliases:
                for v in aliases[k]:
                    self._aliases[v] = k
        self.creation_kwargs['aliases'] = aliases

    def map_value(self, instance, value):
        self._aliases[value]
        return self._map[self._aliases[value]]
