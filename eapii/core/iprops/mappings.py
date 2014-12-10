# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" Property for scalars values such float, int, string, etc...

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
    def __init__(self, getter=None, setter=None, secur_com=0, mapping={}):
        super(Mapping, self).__init__(getter, setter, secur_com)
        self._map = mapping
        self._imap = {v: k for k, v in mapping.items()}

    def post_get(self, instance, value):
        return self._imap[value]

    def pre_set(self, instance, value):
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
    def __init__(self, getter=None, setter=None, secur_com=0, mapping={},
                 aliases={}):
        super(Bool, self).__init__(getter, setter, secur_com, mapping)
        self._aliases = {True: True, False: False}
        if aliases:
            for k in aliases:
                for v in aliases[k]:
                    self._aliases[v] = k

    def pre_set(self, instance, value):
        return self._map[self._aliases[value]]
