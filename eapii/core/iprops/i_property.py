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
from types import MethodType

from ..errors import InstrIOError


def get_chain(iprop, instance):
    """Generic get chain for IProperties.

    """
    i = -1
    while i < iprop._secur:
        try:
            i += 1
            val = iprop.get(instance)
            break
        except instance.secure_com_exceptions:
            if i != iprop._secur:
                instance.reopen_connection()
                continue
            else:
                raise
    alt_val = iprop.post_get(instance, val)

    return alt_val


def set_chain(iprop, instance, value):
    """Generic set chain for IProperties.


    """
    i_val = iprop.pre_set(instance, value)
    i = -1
    while i < iprop._secur:
        try:
            i += 1
            iprop.set(instance, i_val)
            break
        except instance.secure_com_exceptions:
            if i != iprop._secur:
                instance.reopen_connection()
                continue
            else:
                raise
    iprop.post_set(instance, value, i_val)


class IProperty(property):
    """Descriptor representing the most basic instrument property.

    IProperties should not be used outside the definition of a class to avoid
    weird behaviour when some methods are customized.
    IProperty are not meant to be used when writing a driver as it is a bit
    bare, one should rather use the more specialised found in other modules
    of the iprops package.

    When subclassing an IProperty a number of rule should be enforced :
    - the subclass should accept all the parameters from the base class
    - all creation arguments must be stored in creation_kwargs. Failing to do
    this will result in the impossibility to use set_iprop_paras.

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

    Attributes
    ----------
    name : unicode
        Name of the IProperty. This is set by the HasIProps instance and
        should not be manipulated by user code.
    creation_kwargs : dict
        Dictionary in which all the creation args should be stored to allow
        subclass customisation. This should not be manipulated by user code.

    """
    def __init__(self, getter=None, setter=None, secure_comm=0):
        self._getter = getter
        self._setter = setter
        self._secur = secure_comm
        # Don't create the weak values dict if it is not used.
        self._proxies = ()
        self.creation_kwargs = {'getter': getter, 'setter': setter,
                                'secure_comm': secure_comm}

        super(IProperty, self).__init__(fget=self._get if getter else None,
                                        fset=self._set if setter else None)

        self.name = ''

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
        return instance.default_get_iproperty(self, self._getter)

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
        instance.default_set_iproperty(self, self._setter, value)

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
        res, _ = instance.default_check_instr_operation(self)
        if not res:
            mess = 'The instrument did not succeeded to set {} to {} ({}).'
            raise InstrIOError(mess.format(self._name, value, i_value))

    def clone(self):
        """Clone the IProperty by copying all the local attributes and instance
        methods

        """
        p = self.__class__(self._getter, self._setter, secure_comm=self._secur)
        p.__doc__ = self.__doc__

        for k, v in self.__dict__.items():
            if isinstance(v, MethodType):
                setattr(p, k, MethodType(v.__func__, p))
            else:
                setattr(p, k, v)

        return p

    def _get(self, instance):
        """Getter defined when the user provides a value for the get arg.

        """
        with instance.lock:
            cache = instance._cache
            name = self.name
            if name in cache:
                return cache[name]

            if instance in self._proxies:
                return self._proxies[instance].proxy_get(instance)

            val = get_chain(self, instance)
            if name in instance._caching_permissions:
                cache[name] = val

            return val

    def _set(self, instance, value):
        """Setter defined when the user provides a value for the set arg.

        """
        with instance.lock:
            cache = instance._cache
            name = self.name
            if name in cache and value == cache[name]:
                return

            if instance in self._proxies:
                return self._proxies[instance].proxy_set(instance, value)

            set_chain(self, instance, value)
            if name in instance._caching_permissions:
                cache[name] = value
