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
from ..unit import get_unit_registry


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
    def __init__(self, getter=None, setter=None, secure_comm=0, checks=None,
                 values=()):
        super(Enumerable, self).__init__(getter, setter, secure_comm)
        self.values = set(values)
        if setter and values:
            self._wrap_with_checker(self.validate_in, 'pre_set')
        self.creation_kwargs['values'] = values

    def validate_in(self, instance, value):
        """Check the provided values is in the supported values.

        """
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
    def __init__(self, getter=None, setter=None, secure_comm=0, check=None,
                 range=None):
        super(RangeValidated, self).__init__(getter, setter, secure_comm)
        if range:
            wrap = self._wrap_with_checker
            if isinstance(range, AbstractRangeValidator):
                self.range = range
                wrap(self.validate_range, 'pre_set')
            elif istext(range):
                self.range_id = range
                wrap(self.get_range_and_validate, 'pre_set')
            else:
                mess = cleandoc('''The range kwarg should either be a range
                    validator or a string used to retrieve the range through
                    get_range''')
                raise TypeError(mess)
        self.creation_kwargs['range'] = range

    def validate_range(self, obj, value):
        """Make sure a value is in the given range.

        This method is meant to be used as a pre-set.

        """
        if not self.range.validate(value):
            mess = 'The provided value {} is out of bound for {}.'
            mess = mess.format(value, self.name)
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
        return self.validate_range(obj, value)


class Int(RangeValidated, Enumerable):
    """ Property casting the instrument answer to an int.

    Support enumeration or range validation (the range takes precedence).

    """
    def __init__(self, getter=None, setter=None, secure_comm=0, checks=None,
                 values=(), range=None):
        if values and not range:
            Enumerable.__init__(self, getter, setter, secure_comm, checks,
                                values)
        else:
            super(Int, self).__init__(getter, setter, secure_comm, checks,
                                      range)

    def post_get(self, instance, value):
        """Cast the value returned by the instrument to an int.

        """
        return int(value)


class Float(RangeValidated, Enumerable):
    """ Property casting the instrument answer to a float or Quantity.

    Support range validation and unit conversion.

    """
    def __init__(self, getter=None, setter=None, secure_comm=0, checks=None,
                 values=(), range=None, unit=None):
        if values and not range:
            Enumerable.__init__(self, getter, setter, secure_comm, checks,
                                values)
        else:
            super(Float, self).__init__(getter, setter, secure_comm, checks,
                                        range)

        if unit:
            ureg = get_unit_registry()
            self.unit = ureg.parse_expression(unit)
        else:
            self.unit = None

        if range or values:
            self._validate = self.pre_set
            del self.pre_set
            if unit:
                self.pre_set = self.convert_and_validate
            else:
                self.pre_set = self.validate
        else:
            if unit:
                self.pre_set = self.convert

        self.creation_kwargs.update({'unit': unit, 'values': values,
                                     'range': range})

    def post_get(self, instance, value):
        """Cast the value returned by the instrument to float or Quantity.

        """
        fval = float(value)
        if self.unit:
            return fval*self.unit

        else:
            return fval

    def convert_and_validate(self, instance, value):
        """Convert unit and check value.

        This method is meant to be used as a pre_set replacement. When
        overriding pre_set it should be used when both unit and range are
        present.

        """
        if isinstance(value, _Quantity):
            value = value.to(self.unit)
            self._validate(instance, value)
            value = value.magnitude

        else:
            self._validate(instance, value*self.unit)

        return value

    def convert(self, instance, value):
        """Convert unit.

        This method is meant to be used as a pre_set replacement. When
        overriding pre_set it should be used when only unit is present.

        """
        if isinstance(value, _Quantity):
            value = value.to(self.unit).magnitude

        return value

    def validate(self, instance, value):
        """Validate the value.

        This method is meant to be used as a pre_set replacement. When
        overriding pre_set it should be used when only range is present.

        """
        self._validate(instance, value)
        if isinstance(value, _Quantity):
            value = value.magnitude

        return value

    def validate_in(self, instance, value):
        """Check the provided values is in the supported values.

        """
        if isinstance(value, _Quantity):
            value = value.magnitude

        return Enumerable.validate_in(self, instance, value)
