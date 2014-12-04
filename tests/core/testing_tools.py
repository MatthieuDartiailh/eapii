# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Module defining some common tools for testing eapii core.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from threading import RLock

from eapii.core.has_i_props import HasIProps


class Parent(HasIProps):

    def __init__(self):
        super(Parent, self).__init__()
        self.d_get_called = 0
        self.d_get_cmd = None
        self.d_get_args = ()
        self.d_get_kwargs = {}
        self.d_set_called = 0
        self.d_set_cmd = None
        self.d_get_args = ()
        self.d_get_kwargs = {}
        self.d_check_instr = 0
        self.ropen_called = 0
        self.lock = RLock()

    def default_get_iproperty(self, cmd, *args, **kwargs):
        self.d_get_called += 1
        self.d_get_cmd = cmd
        self.d_get_args = args
        self.d_get_kwargs = kwargs
        return cmd

    def default_set_iproperty(self, cmd, *args, **kwargs):
        self.d_set_called += 1
        self.d_set_cmd = cmd
        self.d_set_args = args
        self.d_set_kwargs = kwargs

    def default_check_instr_operation(self):
        self.d_check_instr += 1
        return True, None

    def reopen_connection(self):
        self.ropen_called += 1
