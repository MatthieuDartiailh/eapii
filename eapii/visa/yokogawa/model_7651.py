# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Yokogawa 7651 driver.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from eapii.core.api import set_iprop_paras, FloatRangeValidator
from eapii.core.iprops.api import Float, Bool, Mapping
from eapii.visa.api import VisaMessageInstrument, Register


VOLT_RANGE = {30.0: 6,
              10.0: 5,
              1.0: 4,
              0.1: 3,
              0.01: 2}

VOLT_STEP = {30.0: 1e-3,
             10.0: 0.1e-3,
             1.0: 0.01e-3,
             0.1: 1e-6,
             0.01: 0.1e-6}

CURR_RANGE = {1.0: 4,
              10.0: 5,
              100.0: 6}


CURR_STEP = {100.0: 1e-3,
             10.0: 0.1e-3,
             1.0: 0.01e-3}


class Yokogawa7651(VisaMessageInstrument):
    """Driver for the Yokogawa 7651.

    """
    protocoles = {'GPIB': 'INSTR', 'ASRL': 'INSTR'}

    caching_permissions = {'function': True, 'output': True,
                           'voltage': True, 'voltage_range': True,
                           'current': True, 'current_range': True}

    # =========================================================================
    # --- IProperties
    # =========================================================================

    #: Operation mode of the instrument.
    function = Mapping(True, 'F{}',
                       mapping={'Voltage': 1, 'Current': 5},
                       secure_comm=2)

    #: State of the output expressed as a boolean.
    output = Bool(True, 'O{}',
                  mapping={True: 1, False: 0},
                  aliases={True: ['ON'], False: ['OFF']},
                  secure_comm=2)

    #: Currently applied voltage in V. Apply only if function is 'Voltage'.
    voltage = Float(True, 'S{:+E}E', unit='V',
                    checks='{function} == "Voltage"',
                    range='voltage_range',
                    secure_comm=2)

    #: Current voltage range in V. Apply only if function is 'Voltage'.
    voltage_range = Float(True, True, unit='V',
                          checks='{function} == "Voltage"',
                          values=(0.01, 0.1, 1.0, 10.0, 30.0),
                          secure_comm=2)

    #: Currently delivered current in mA. Apply only if function is 'Current'.
    current = Float(True, 'S{:+E}E', unit='mA',
                    checks='{function} == "Current"',
                    range='current_range',
                    secure_comm=2)

    #: Current current range in mA. Apply only if function is 'Voltage'.
    current_range = Float(True, True, unit='mA',
                          checks='{function} == "Current"',
                          values=(1.0, 10.0, 100.0),
                          secure_comm=2)

    #: Status code of the instrument.
    status_code = Register('OC', names=('Program setting',
                                        'Program under execution',
                                        'Error', 'Output stable', 'Output',
                                        'Cal mode', 'IC card', 'CAL switch'))

    status_byte = set_iprop_paras(names=('Output stable', 'SRQ on',
                                         'Syntax error', 'Limit error',
                                         'Program end', 'Error', 'SRQ', None))

    # =========================================================================
    # --- Methods
    # =========================================================================

    def default_check_instr_operation(self, iprop, value, i_value):
        """Check the instrument status byte for errors.

        If the error queue is found to contains error messages, those are
        queried and returned as details.

        """
        if self.status_byte['Error']:
            return False, ''

        return True, None

    # =========================================================================
    # --- IProperty customisation
    # =========================================================================

    def _get_function(self, iprop):
        return 1 if self.query('OD')[3] == 'V' else 5

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

    def _get_output(self, iprop):
        return self.status_code['Output']

    def _get_voltage(self, iprop):
        return self.query('OD')[4:]

    def _get_voltage_range(self, iprop):
        self.query('OS')
        aux = self.read()
        self.read()
        self.read()
        self.read()
        return [k for k, v in VOLT_RANGE.items() if v == int(aux[3])][0]

    def _set_voltage_range(self, iprop, value):
        self.write('R{}'.format(VOLT_RANGE[value]))

    def _post_set_voltage_range(self, iprop, value, i_value):
        self.discard_range('voltage_range')
        self.default_check_instr_operation(self, iprop, value, i_value)

    def _range_voltage_range(self):
        val = self.voltage_range.magnitude
        if val == 30.0:
            return FloatRangeValidator(-32.0, 32.0, VOLT_STEP[val], 'V')
        else:
            return FloatRangeValidator(-1.2*val, 1.2*val, VOLT_STEP[val], 'V')

    def _get_current(self, iprop):
        return self.query('OD')[4:]

    def _get_current_range(self, iprop):
        self.query('OS')
        aux = self.read()
        self.read()
        self.read()
        self.read()
        return [k for k, v in CURR_RANGE.items() if v == int(aux[3])][0]

    def _set_current_range(self, iprop, value):
        self.write('R{}'.format(CURR_RANGE[value]))

    def _post_set_current_range(self, iprop, value, i_value):
        self.discard_range('current_range')
        self.default_check_instr_operation(self, iprop, value, i_value)

    def _range_current_range(self):
        val = self.current_range.magnitude
        if val == 200.0:
            return FloatRangeValidator(-200.0, 200.0, CURR_STEP[val], 'mA')
        else:
            return FloatRangeValidator(-1.2*val, 1.2*val, CURR_STEP[val], 'mA')
