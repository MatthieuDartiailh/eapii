# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Yokogawa GS200 driver.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from eapii.core.api import set_iprop_paras, FloatRangeValidator
from eapii.core.iprops.api import Float, Bool, Mapping
from eapii.visa.api import IEC60488


VOLT_STEP = {30.0: 1e-3,
             10.0: 0.1e-3,
             1.0: 0.01e-3,
             0.1: 1e-6,
             0.01: 0.1e-6}


CURR_STEP = {200.0: 1e-3,
             100.0: 1e-3,
             10.0: 0.1e-3,
             1.0: 0.01e-3}


class YokogawaGS200(IEC60488):
    """Driver for the Yokogawa GS200.

    """
    protocoles = {'GPIB': 'INSTR', 'USB': 'INSTR', 'TCPIP': 'INSTR'}

    caching_permissions = {'function': True, 'outout': True,
                           'voltage': True, 'voltage_range': True,
                           'current': True, 'current_range': True}

    # =========================================================================
    # --- IProperties
    # =========================================================================

    #: Operation mode of the instrument.
    function = Mapping('SOURce:FUNCtion?', 'SOURce:FUNCtion {}',
                       mapping={'Voltage': 'VOLT', 'Current': 'CURR'},
                       secure_comm=2)

    #: State of the output expressed as a boolean.
    output = Bool(':OUTPUT?', ':OUTPUT {}',
                  mapping={True: 'ON', False: 'OFF'},
                  aliases={True: ['ON'], False: ['OFF']},
                  secure_comm=2)

    #: Currently applied voltage in V. Apply only if function is 'Voltage'.
    voltage = Float(':SOURce:LEVel?', ':SOURce:LEVel {}', unit='V',
                    checks='{function} == "Voltage"',
                    range='voltage_range',
                    secure_comm=2)

    #: Current voltage range in V. Apply only if function is 'Voltage'.
    voltage_range = Float(':SOURce:RANGe?', ':SOURce:RANGe {}', unit='V',
                          checks='{function} == "Voltage"',
                          values=(0.01, 0.1, 1.0, 10.0, 30.0),
                          secure_comm=2)

    #: Currently delivered current in mA. Apply only if function is 'Current'.
    current = Float(':SOURce:LEVel?', ':SOURce:LEVel {}', unit='mA',
                    checks='{function} == "Current"',
                    range='current_range',
                    secure_comm=2)

    #: Current current range in mA. Apply only if function is 'Voltage'.
    current_range = Float(':SOURce:RANGe?', ':SOURce:RANGe {}', unit='mA',
                          checks='{function} == "Current"',
                          values=(1.0, 10.0, 100.0, 200.0),
                          secure_comm=2)

    status_byte = set_iprop_paras(names={'Extended event summary': 1,
                                         'Error available': 2,
                                         'Message available': 4,
                                         'Event summary': 5,
                                         'Request service': 6})

    # =========================================================================
    # --- Methods
    # =========================================================================

    def default_check_instr_operation(self, iprop, value, i_value):
        """Check the instrument status byte for errors.

        If the error queue is found to contains error messages, those are
        queried and returned as details.

        """
        errors = []
        while self.status_byte['Error available']:
            errors.append(self.query(':STAT:ERR?'))

        return bool(errors), '\n'.join(errors)

    # =========================================================================
    # --- IProperty customisation
    # =========================================================================

    def _post_set_function(self, iprop, value, i_value):
        """Clear the cache of affected property.

        """
        del self.current
        del self.current_range
        self.discard_range('current_range')
        del self.voltage
        del self.voltage_range
        self.discard_range('voltage_range')
        self.default_check_instr_operation(self, iprop, value, i_value)

    def _post_set_voltage_range(self, iprop, value, i_value):
        self.discard_range('voltage_range')
        self.default_check_instr_operation(self, iprop, value, i_value)

    def _range_voltage_range(self):
        val = self.voltage_range.magnitude
        if val == 30.0:
            return FloatRangeValidator(-32.0, 32.0, VOLT_STEP[val], 'V')
        else:
            return FloatRangeValidator(-1.2*val, 1.2*val, VOLT_STEP[val], 'V')

    def _post_set_current_range(self, iprop, value, i_value):
        self.discard_range('current_range')
        self.default_check_instr_operation(self, iprop, value, i_value)

    def _range_current_range(self):
        val = self.current_range.magnitude
        if val == 200.0:
            return FloatRangeValidator(-200.0, 200.0, CURR_STEP[val], 'mA')
        else:
            return FloatRangeValidator(-1.2*val, 1.2*val, CURR_STEP[val], 'mA')
