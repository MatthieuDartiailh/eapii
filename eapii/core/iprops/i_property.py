# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" Base descriptor for all instrument properties declaration.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from contextlib import contextmanager
from types import MethodType

from ..errors.api import InstrIOError


class IProperty(object):
    """Descriptor representing the most basic instrument property.

    IProperty are not meant to be used when writing a driver as it is a bit
    bare, one should rather use the more specialised found in other modules
    of the iprops package.

    Parameters
    ----------
    getter : optional
        Object used to access the instrument property value through the use
        of the driver. If absent the IProperty will be considered write only.
        This is typically a string.
    setter : optional
        Object used to set the instrument property value through the use
        of the driver. If absent the IProperty will be considered read-only.
        This is typically a string.
    secure_comm : int, optional
        Whether or not a failed communication should result in a new attempt
        to communicate after re-opening the communication. The value is used to
        determine how many times to retry.

    """
    def __init__(self, getter=None, setter=None, secure_comm=0):
        self._get = getter
        self._set = setter
        self._secur = secure_comm

        if getter:
            self.__get__ = self._get

        if setter:
            self.__set__ = self._set

    def get(self, instance):
        """Acces the parent driver to retrieve the state of the instrument.

        By default this method falls back to calling the parent
        default_get_iproperty method. This behaviour can be customized by
        creating a _get_(iprop name) method on the driver class.

        Parameters
        ----------
        instance : HasIProp
            Instrument or SubSystem object on which this IProperty is defined.

        Returns
        -------
        value :
            The value as returned by the query method. If any formatting is
            necessary it should be done in the post_get method.

        """
        if self._secur:
            with self.secure_communication(instance):
                return instance.default_get_iproperty(self.getter)
        else:
            return instance.default_get_iproperty(self.getter)

    def post_get(self, instance, value):
        """Hook to alter the value returned by the underlying driver.

        This can be used to convert the answer from the instrument to a more
        human friendly representation. By default this is a no-op. This
        behaviour can be customized by creating a _post_get_(iprop name) method
        on the driver class.

        Parameters
        ----------
        instance : HasIProp
            Instrument or SubSystem object on which this IProperty is defined.
        value :
            Value as returned by the underlying driver.

        Returns
        -------
        formatted_value :
            Formatted value.

        """
        return value

    def pre_set(self, instance, value):
        """Hook to format the value passed to the IProperty before sending it
        to the instrument.

        This can be used to convert the passed value to something easier to
        pass to the instrument. By default this is a no-op. This behaviour can
        be customized by creating a _pre_set_(iprop name) method on the driver
        class.

        Parameters
        ----------
        instance : HasIProp
            Instrument or SubSystem object on which this IProperty is defined.
        value :
            Value as passed by the user.

        Returns
        -------
        i_value :
            Value which should be passed to the set method.

        """
        return value

    def set(self, instance, value):
        """Access the driver to actuallyt set the instrument state.

        By default this method falls back to calling the parent
        default_set_iproperty method. This behaviour can be customized by
        creating a _set_(iprop name) method on the driver class.

        Parameters
        ----------
        instance : HasIProp
            Instrument or SubSystem object on which this IProperty is defined.
        value :
            Object to pass to the driver method to set the value.

        """
        instance.default_set_iproperty(self.setter, value)

    def post_set(self, instance, value, i_value):
        """Hook to perform additional action after setting a value.

        This can be used to check the instrument operated correctly or perform
        some cleanup. By default this falls back on the driver
        default_check_instr_operation method. This behaviour can be customized
        by creating a _post_set_(iprop name) method on the driver class.

        Parameters
        ----------
        instance : HasIProp
            Instrument or SubSystem object on which this IProperty is defined.
        value :
            Value as passed by the user.
        i_value :
            Value which was passed to the set method.

        Raises
        ------
        InstrIOError :
            Raised if the driver detects an issue.

        """
        res, _ = instance.default_check_instr_operation()
        if not res:
            mess = 'The instrument did not succeeded to set {} to {} ({}).'
            raise InstrIOError(mess.format(self._name, value, i_value))

    @contextmanager
    def secure_communication(self, instance):
        """Make sure a communication issue cannot simply be resolved by
        re-opening the communication.

        Parameters
        ----------
        instance : HasIProps
             Instrument or SubSystem object on which this IProperty is defined.

        """
        i = -1
        while i < self._secur:
            try:
                i += 1
                yield
            except instance.secure_comm_exceptions as e:
                if i != self._secur:
                    instance.reopen_connection()
                    continue
                else:
                    raise

    def set_name(self, name):
        """Set the name of the IProp used in errors messages.

        """
        self._name = name

    def _get(self, instance, type=None):
        """Getter defined when the user provides a value for the get arg.

        """
        if not type:
            return self

        with self.secure_communication(instance):
            val = self.get(instance)
        alt_val = self.post_get(instance, val)
        return val

    def _set(self, instance, value):
        """Setter defined when the user provides a value for the set arg.

        """
        i_val = self.pre_set(instance, value)
        with self.secure_communication(instance):
            self.set(instance, i_val)
        self.post_set(instance, value, i_value)
