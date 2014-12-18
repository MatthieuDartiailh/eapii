# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" Module defining the range utilities used for int and float.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from types import MethodType
from math import modf
from functools import update_wrapper
from pint.quantity import _Quantity

from .unit import get_unit_registry


class AbstractRangeValidator(object):
    """ Base class for all range validators.

    Attribute
    ---------
    minimum :
        Minimal allowed value or None.
    maximum :
        Maximal allowed value or None.
    step :
        Allowed step between values or None.

    Methods
    -------
    validate :
        Validate a given value against the range.

    """
    __slots__ = ('minimum', 'maximum', 'step', 'validate')


class IntRangeValidator(AbstractRangeValidator):
    """Range used to validate a the value of an integer.

    Parameters
    ----------
    min : int, optional
        Minimal allowed value
    max : int, optional
        Maximum allowed value
    step : int, optional
        Smallest allowed step

    Methods
    -------
    validate :
        Validate a given value. If a unit is declared both floats and Quantity
        can be passed.

    """

    __slots__ = ()

    def __init__(self, min=None, max=None, step=None):
        mess = 'The {} of an IntRange must be an integer not {}.'
        if min is None and max is None:
            raise ValueError('An IntRangeValidator must have a min or max')
        if min is not None and not isinstance(min, int):
            raise TypeError(mess.format('min', type(min)))
        if max is not None and not isinstance(max, int):
            raise TypeError(mess.format('max', type(max)))
        if step and not isinstance(step, int):
            raise TypeError(mess.format('step', type(step)))

        self.minimum = min
        self.maximum = max
        self.step = step

        if min is not None:
            if max is not None:
                if step:
                    self.validate = self._validate_range_and_step
                else:
                    self.validate = self._validate_range
            else:
                if step:
                    self.validate = self._validate_larger_and_step
                else:
                    self.validate = self._validate_larger
        else:
            if step:
                self.validate = self._validate_smaller_and_step
            else:
                self.validate = self._validate_smaller

    def _validate_smaller(self, value):
        """Check if the value is smaller than the maximum.

        """
        return value <= self.maximum

    def _validate_smaller_and_step(self, value):
        """Check if the value is smaller than the maximum and respect the step.

        """
        return value <= self.maximum and (value-self.maximum) % self.step == 0

    def _validate_larger(self, value):
        """Check if the value is larger than the minimum.

        """
        return value >= self.minimum

    def _validate_larger_and_step(self, value):
        """Check if the value is larger than the minimum and respect the step.

        """
        return value >= self.minimum and (value-self.minimum) % self.step == 0

    def _validate_range(self, value):
        """Check if the value is in the range.

        """
        return self.minimum <= value <= self.maximum

    def _validate_range_and_step(self, value):
        """Check if the value is in the range and respect the step.

        """
        return self.minimum <= value <= self.maximum\
            and (value-self.minimum) % self.step == 0


class FloatRangeValidator(AbstractRangeValidator):
    """Range used to validate a the value of an integer.

    Parameters
    ----------
    min : float, optional
        Minimal allowed value
    max : float, optional
        Maximum allowed value
    step : float, optional
        Smallest allowed step
    unit : str, optional
        Unit in which the bounds and step are expressed.

    Attributes
    ----------
    unit : Unit or None
        Unit used when validating.

    Methods
    -------
    validate :
        Validate a given value. If a unit is declared both floats and Quantity
        can be passed.

    """

    __slots__ = ('unit')

    def __init__(self, min=None, max=None, step=None, unit=None):
        mess = 'The {} of an IntRange must be an integer not {}.'
        if min is None and max is None:
            raise ValueError('An IntRangeValidator must have a min or max')
        if min is not None and not isinstance(min, float):
            raise TypeError(mess.format('min', type(min)))
        if max is not None and not isinstance(max, float):
            raise TypeError(mess.format('max', type(max)))
        if step and not isinstance(step, float):
            raise TypeError(mess.format('step', type(step)))

        self.minimum = min
        self.maximum = max
        self.step = step

        if unit:
            ureg = get_unit_registry()
            self.unit = ureg.parse_expression(unit)
            wrap = self._unit_conversion
        else:
            wrap = lambda x: x

        if min is not None:
            if max is not None:
                if step:
                    self.validate = wrap(self._validate_range_and_step)
                else:
                    self.validate = wrap(self._validate_range)
            else:
                if step:
                    self.validate = wrap(self._validate_larger_and_step)
                else:
                    self.validate = wrap(self._validate_larger)
        else:
            if step:
                self.validate = wrap(self._validate_smaller_and_step)
            else:
                self.validate = wrap(self._validate_smaller)

    def _unit_conversion(self, cmp_func):
        """Decorator handling unit conversion to the unit.

        """
        if isinstance(cmp_func, MethodType):
            cmp_func = cmp_func.__func__

        def wrapper(self, value):
            if not isinstance(value, _Quantity):
                return cmp_func(self, value)

            else:
                return cmp_func(self, value.to(self.unit).magnitude)

        update_wrapper(wrapper, cmp_func)
        wrapper.__doc__ += '\nAutomatic handling of unit conversions'
        return MethodType(wrapper, self)

    def _validate_smaller(self, value):
        """Check if the value is smaller than the maximum.

        """
        return value <= self.maximum

    def _validate_smaller_and_step(self, value):
        """Check if the value is smaller than the maximum and respect the step.

        """
        ratio = round(abs((value-self.maximum)/self.step), 9)
        return value <= self.maximum and modf(ratio)[0] < 1e-9

    def _validate_larger(self, value):
        """Check if the value is larger than the minimum.

        """
        return value >= self.minimum

    def _validate_larger_and_step(self, value):
        """Check if the value is larger than the minimum and respect the step.

        """
        ratio = round(abs((value-self.minimum)/self.step), 9)
        return value >= self.minimum and modf(ratio)[0] < 1e-9

    def _validate_range(self, value):
        """Check if the value is in the range.

        """
        return self.minimum <= value <= self.maximum

    def _validate_range_and_step(self, value):
        """Check if the value is in the range and respect the step.

        """
        ratio = round(abs((value-self.minimum)/self.step), 9)
        return self.minimum <= value <= self.maximum\
            and abs(modf(ratio)[0]) < 1e-9
