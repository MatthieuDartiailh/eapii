# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" Subsystems can be used to give a hierarchical organisation to a driver.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from future.utils import with_metaclass

from .has_i_props import HasIPropsMeta, HasIProps


class DeclarationMeta(HasIPropsMeta):
    """Metaclass used to avoid creating an instance in classes declaration.

    """
    def __call__(self, *args, **kwargs):
        """ Create a new instance only if a parent is passed as first argument.

        """
        if not args:
            return self
        else:
            return super(DeclarationMeta, self).__call__(*args, **kwargs)


class SubSystem(with_metaclass(DeclarationMeta, HasIProps)):
    """SubSystem allow to split the implementation of a driver into multiple
    parts.

    This mechanism allow to avoid crowding the instrument namespace with very
    long IProperty names, for example.

    """
    def __init__(self, parent, **kwargs):
        super(SubSystem, self).__init__(**kwargs)
        self.parent = parent

    @property
    def lock(self):
        return self.parent.lock

    def reopen_connection(self):
        """Subsystems simply pipes the call to their parent.

        """
        self.parent.reopen_connection()

    def default_get_iproperty(self, cmd, *args, **kwargs):
        """Subsystems simply pipes the call to their parent.

        """
        return self.parent.default_get_iproperty(cmd, *args, **kwargs)

    def default_set_iproperty(self, cmd):
        """Subsystems simply pipes the call to their parent.

        """
        return self.parent.default_set_iproperty(cmd, *args, **kwargs)

    def default_check_instr_operation(self):
        """Subsystems simply pipes the call to their parent.

        """
        return self.parent.default_check_instr_operation()
