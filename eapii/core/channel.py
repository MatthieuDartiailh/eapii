# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" Channel simplifies the writing of instrument implementing channel specific
behaviour.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from .has_i_props import AbstractChannel
from .subsystem import SubSystem


class Channel(SubSystem):
    """Channels are used to represent instrument channels identified by a id
    (a number generally).

    They are similar to SubSystems in that they expose a part of the
    instrument capabilities but multiple instances of the same channel
    can exist at the same time under the condition that they have different
    ids.

    By default channels passes their id to their parent when they call
    default_*_iproperty as the kwarg 'ch_id' which can be used by the parent
    to direct the call to the right channel.

    Parameters
    ----------
    parent : HasIProp
        Parent object which can be the concrete driver or a subsystem or
        channel.
    id :
        Id of the channel used by the instrument to correctly route the calls.

    Attributes
    ----------
    id :
        Id of the channel used by the instrument to correctly route the calls.

    """
    def __init__(self, parent, id, **kwargs):
        super(Channel, self).__init__(parent, **kwargs)
        self.id = id

    @property
    def lock(self):
        """Access parent lock."""
        return self.parent.lock

    def default_get_iproperty(self, iprop, cmd, *args, **kwargs):
        """Channels simply pipes the call to their parent.

        """
        kwargs['ch_id'] = self.id
        return self.parent.default_get_iproperty(iprop, cmd, *args, **kwargs)

    def default_set_iproperty(self, iprop, cmd, *args, **kwargs):
        """Channels simply pipes the call to their parent.

        """
        kwargs['ch_id'] = self.id
        return self.parent.default_set_iproperty(iprop, cmd, *args, **kwargs)

    def default_check_instr_operation(self, iprop, value, i_value):
        """Channels simply pipes the call to their parent.

        """
        return self.parent.default_check_instr_operation(iprop, value, i_value)

AbstractChannel.register(Channel)
