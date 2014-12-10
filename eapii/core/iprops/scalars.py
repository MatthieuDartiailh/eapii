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
# Used to get a 2/3 independent unicode conversion.
from future.builtins import str as ustr
from future.utils import istext
from inspect import cleandoc
from pint.quantity import _Quantity

from .i_property import IProperty
from ..range import AbstractRangeValidator
from ..unit import get_ureg


class Enumerable(IProperty):
    """ Validate set value against a finite set of allowed ones.

    Parameters
    ----------
    getter : optional
        Object used to access the instrument property value through the use
        of the driver. If absent the IProperty will be considered write only.
        This is typically a string. If the default get behaviour is overwritten
        True should be passed to mark the property as readable.
    setter : optional
        Object used to set the instrument property value through the use
        of the driver. If absent the IProperty will be considered read-only.
        This is typically a string. If the default set behaviour is overwritten
        True should be passed to mark the property as settable.
    secure_comm : int, optional
        Whether or not a failed communication should result in a new attempt
        to communicate after re-opening the communication. The value is used to
        determine how many times to retry.
    values : iterable, optional
        Permitted values for the property.

    """
    def __init__(self, getter=None, setter=None, secur_com=0, values=()):
        super(IProperty, self).__init__(getter, setter, secur_com)
        self.values = set(values)
        if setter and values:
            self.pre_set = self.validate_in

    def validate_in(self, instance, value):
        if value not in self.values:
            mess = 'Allowed value for {} are {}, {} not allowed'
            raise ValueError(mess.format(self.name, self.values, value))

        return value


class Unicode(Enumerable):
    """ Property casting the instrument answer to a unicode, support
    enumeration.

    Parameters
    ----------
    getter : optional
        Object used to access the instrument property value through the use
        of the driver. If absent the IProperty will be considered write only.
        This is typically a string. If the default get behaviour is overwritten
        True should be passed to mark the property as readable.
    setter : optional
        Object used to set the instrument property value through the use
        of the driver. If absent the IProperty will be considered read-only.
        This is typically a string. If the default set behaviour is overwritten
        True should be passed to mark the property as settable.
    secure_comm : int, optional
        Whether or not a failed communication should result in a new attempt
        to communicate after re-opening the communication. The value is used to
        determine how many times to retry.

    """
    def post_get(self, instance, value):
        return ustr(value)


class RangeValidated(IProperty):
    """ Property checking the given value is in the right range before setting.

    Parameters
    ----------
    getter : optional
        Object used to access the instrument property value through the use
        of the driver. If absent the IProperty will be considered write only.
        This is typically a string. If the default get behaviour is overwritten
        True should be passed to mark the property as readable.
    setter : optional
        Object used to set the instrument property value through the use
        of the driver. If absent the IProperty will be considered read-only.
        This is typically a string. If the default set behaviour is overwritten
        True should be passed to mark the property as settable.
    secure_comm : int, optional
        Whether or not a failed communication should result in a new attempt
        to communicate after re-opening the communication. The value is used to
        determine how many times to retry.
    range : RangeValidator or str
        If a RangeValidator is provided it is used as is, if a string is
        provided it is used to retrieve the range from the driver at runtime.

    """
    def __init__(self, getter=None, setter=None, secur_com=0,  range=None):
        super(RangeValidated, self).__init__(getter, setter, secur_com)
        if range:
            if isinstance(range, AbstractRangeValidator):
                self.range = range
                self.pre_set = self.validate_range
            elif istext(range):
                self.range_id = range
                self.pre_set = self.get_range_and_validate
            else:
                mess = cleandoc('''The range kwarg should either be a range
                    validator or a string used to retrieve the range through
                    get_range''')
                raise TypeError(mess)

    def validate_range(self, obj, value):
        """Make sure a value is in the given range.

        This method is meant to be used as a pre-set.

        """
        if not self.range.validate(value):
            mess = 'The provided value {} is out of bound for {}.'
            ran = self.range
            if ran.minimum:
                mess += ' Minimum {}.'.format(ran.minimum)
            if ran.maximum:
                mess += ' Maximum {}.'.format(ran.maximum)
            if ran.step:
                mess += ' Step {}.'.format(ran.step)
            raise ValueError(mess)
        else:
            return value

    def get_range_and_validate(self, obj, value):
        """Query the current range from the driver and validate the values.

        This method is meant to be used as a pre-set.

        """
        self.range = obj.get_range(self.range_id)
        return self.validate_value(obj, value)


class Int(RangeValidated, Enumerable):
    """ Property casting the instrument answer to an int.

    Support enumeration or range validation (the range takes precedence).

    """
    def __init__(self, getter=None, setter=None, secur_com=0, values=(),
                 range=None):
        if values:
            Enumerable.__init__(self, getter, setter, secur_com, values)
        else:
            super(RangeValidated, self).__init__(getter, setter, secur_com)

    def post_get(self, instance, value):
        """Cast the value returned by the instrument to an int.

        """
        return int(value)


class Float(RangeValidated):
    """ Property casting the instrument answer to a float or Quantity.

    Support range validation and unit conversion.

    """
    def __init__(self, getter=None, setter=None, secur_com=0, range=None,
                 unit=None):
        super(Float, self).__init__(getter, setter, secur_com, None, range)
        if unit:
            ureg = get_ureg()
            self.unit = ureg.parse_expression(unit)
        else:
            self.unit = None

        if range:
            self._validate = self.pre_set
            del self.pre_set
            self.pre_set = self.validate

    def post_get(self, instance, value):
        """Cast the value returned by the instrument to float or Quantity.

        """
        fval = float(value)
        if self.unit:
            return fval*self.unit

        else:
            return fval

    def validate(self, instance, value):
        """Convert unit and check value.

        This method is meant to be used as a preset.

        """
        if isinstance(value, _Quantity) and self.unit:
            value = value.to(self.unit)
            self._validate(value)
            value = value.magnitude

        else:
            self._validate(value)

        return value
