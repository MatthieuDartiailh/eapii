# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" Module implementing standards compliant drivers.

The drivers defined in this module can be used as based class for instrument
implementing the standard.

This module has been inspired by the iec60488 module found in the slave
project.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from .visa_instrs import VisaMessageInstrument
from .register import Register
from ..core.iprops.api import Bool


EVENT_STATUS_BYTE = (
    'operation complete',
    'request control',
    'query error',
    'device dependent error',
    'execution error',
    'command error',
    'user request',
    'power on',
    )


class IEC60488(VisaMessageInstrument):
    """ Base class for instrument implementing the following commands.

    Reporting Commands
        - `*CLS` - Clears the data status structure.
        - `*ESE` - Write the event status enable register.
        - `*ESE?` - Query the event status enable register.
        - `*ESR?` - Query the standard event status register.
        - `*SRE` - Write the status enable register.
        - `*SRE?` - Query the status enable register.
        - `*STB` - Query the status register.
    Internal operation commands
        - `*IDN?` - Identification query.
        - `*RST` - Perform a device reset.
        - `*TST?` - Perform internal self-test.
    Synchronization commands
        - `*OPC` - Set operation complete flag high.
        - `*OPC?` - Query operation complete flag.
        - `*WAI` - Wait to continue.

    """
    #: Event register recording the state of the different events.
    event_status = Register('*ESR?', '*ESR {}', names=EVENT_STATUS_BYTE)

    #: Register listing ofr which event notifications are enabled.
    event_status_enable = Register('*ESE?', '*ESE {}', names=[None]*8)

    #: Register listing ofr which event service requests are enabled.
    service_request_enable = Register('*SRE?', '*SRE {}', names=[None]*8)

    #: Flag signaling all pending operations are completed.
    operation_complete = Bool('*OPC?', mapping={True: '1', False: '0'})

    def get_id(self):
        """Access the instrument identification."""
        return self.query('*IDN?')

    def clear_status(self):
        """Clears the status data structure."""
        self.write('*CLS')

    def complete_operation(self):
        """Sets the operation complete bit high of the event status byte."""
        self.write('*OPC')

    def reset(self):
        """Performs a device reset."""
        self.write('*RST')

    def test(self):
        """Performs a internal self-test and returns an integer in the range
        -32767 to + 32767.
        """
        return int(self.query('*TST?'))

    def wait_to_continue(self):
        """Prevents the device from executing any further commands or queries
        until the no operation flag is `True`.

        """
        self.write('*WAI')
