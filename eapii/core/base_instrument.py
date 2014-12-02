# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" BaseInstrument defines the common expected interface for all drivers.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from future.utils import with_metaclass
from threading import RLock
from weakref import WeakValueDictionary

from .has_i_props import HasIPropsMeta, HasIProps


class InstrumentSigleton(HasIPropsMeta):
    """Metaclass ensuring that a single driver is created per instrument.

    """

    def __call__(self, connection_infos, caching_alowed=True,
                 caching_permissions={}, auto_open=True):
        # This is done on first call rather than init to avoid useless memory
        # allocation.
        if not hasattr(self, _instances_cache):
            self._instances_cache = WeakValueDictionary()

        cache = self._instances_cache
        driver_id = set(connection_infos.items())
        if driver_id not in cache:
            dr = super(InstrumentSigleton, self).__call__(connection_infos,
                                                          caching_alowed,
                                                          caching_permissions,
                                                          auto_open)

            cache[driver_id] = dr

        return cache[driver_id]


class BaseInstrument(with_metaclass(InstrumentSigleton, HasIProps)):
    """ Base class of all instrument drivers in Eapii.

    This class defines the common interface drivers are expected to implement
    and take care of keeping a single instance for each set of connection
    informations.

    WARNING: The optional arguments will be taken into account only if the
    instance corresponding to the connection infos does not exist.

    Parameters
    ----------
    connection_info : dict
        Dict containing all the necessary information to open a connection to
        the instrument
    caching_allowed : bool, optionnal
        Boolean use to determine if instrument properties can be cached
    caching_permissions : dict(str : bool), optionnal
        Dict specifying which instrument properties can be cached, override the
        default parameters specified in the class attribute.
    auto_open : bool, optional
        Whether to automatically open the connection to the instrument when the
        driver is instantiated.

    """
    secure_com_except = (InstrIOError)

    def __init__(self, connection_info, caching_allowed=True,
                 caching_permissions={}, auto_open=True):
        super(BaseInstrument, self).__init__()
        if caching_allowed:
            # Avoid overriding class attribute
            perms = self.caching_permissions.copy()
            perms.update(caching_permissions)
            self._caching_permissions = set([key for key in perms
                                             if perms[key]])
        else:
            self._caching_permissions = set()

        self.owner = ''
        self.lock = RLock()

    def open_connection(self):
        """Open a connection to an instrument.

        """
        message = fill(cleandoc(
            '''This method is used to open the connection with the
            instrument and should be implemented by classes
            subclassing BaseInstrument.'''),
            80)
        raise NotImplementedError(message)

    def close_connection(self):
        """Close the connection to the instrument.

        """
        message = fill(cleandoc(
            '''This method is used to close the connection with the
            instrument and should be implemented by classes
            subclassing BaseInstrument.'''),
            80)
        raise NotImplementedError(message)

    def check_connection(self):
        """Check whether or not the cache is likely to have been corrupted.

        """
        message = fill(cleandoc(
            '''This method is used to check that the instrument is
            in remote mode and that none of the values in the cache
            has been corrupted by a local user, and should be implemented
            by classes subclassing BaseInstrument'''),
            80)
        raise NotImplementedError(message)

    def connected(self):
        """Return whether or not commands can be sent to the instrument.

        """
        message = fill(cleandoc(
            '''This method returns whether or not command can be
            sent to the instrument, and should be implemented by classes
            subclassing BaseInstrument.'''),
            80)
        raise NotImplementedError(message)
