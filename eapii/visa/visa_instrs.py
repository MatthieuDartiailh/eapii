# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" Module implementing the base drivers for instrument communicating through
the VISA protocol.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from time import sleep

from ..core.iprops.register import Register
from ..core.base_instrument import BaseInstrument
from ..core.errors import InstrIOError
from .visa import get_visa_resource_manager, VisaIOError


class BaseVisaInstrument(BaseInstrument):
    """Base class for instrument communicating through the VISA protocol.

    It handles the connection management, but not the subsequent communication.
    That's why driver should not inherit from it but from one of its derived
    class (save for very peculiar use).

    Parameters
    ----------
    connection_infos : dict
        For a VisaInstrument two entries at least are expected:
            - type : The kind of connection (GPIB, USB, PXI, ...). The board
                     number can be specified too. NB: for serial (ASRL) do not
                     specify the board use the address entry instead.
            - address : The address of the instrument.

        Other entries can be :
            - mode : Mode of connection (INSTR, RAW, SOCKET). If absent INSTR
                     will be assumed.
            - para : a dict to alter the driver attributes.

        Those information will be concatenated using ::.

    caching_allowed : bool, optional
        Boolean use to determine if instrument properties can be cached
    caching_permissions : dict(str : bool), optionnal
        Dict specifying which instrument properties can be cached, override the
        default parameters specified in the class attribute.
    auto_open : bool, optional
        Whether to automatically open the connection to the instrument when the
        driver is instantiated.

    Attributes
    ----------
    protocols : dict
        Class attributes used for introspection purposes, it should specify
        the kind of connection supported by the instrument (GPIB, USB, ...) and
        the mode (INSTR, port::SOCKET, ...)

    """
    secure_com_except = (InstrIOError, VisaIOError)

    protocols = {}

    def __init__(self, connection_infos, caching_allowed=True,
                 caching_permissions={}, auto_open=True):
        super(BaseVisaInstrument, self).__init__(connection_infos,
                                                 caching_allowed,
                                                 caching_permissions,
                                                 auto_open)

        self.connection_str = str(connection_infos['type']
                                  + '::' + connection_infos['address']
                                  + '::' + connection_infos['mode'])
        self._driver = None
        self._para = connection_infos.get('para', {})
        if auto_open:
            self.open_connection()

    @classmethod
    def compute_id(cls, connection_infos):
        """Insert the default mode in the connection_infos to avoid ambiguity
        in the id.

        """
        if not connection_infos.get('mode'):
            connection_infos['mode'] = 'INSTR'

        super(BaseVisaInstrument, cls).compute_id(connection_infos)

    def open_connection(self):
        """Open the VISA session.

        """
        rm = get_visa_resource_manager()
        self._driver = rm.open_resource(self.connection_str, **self._para)

    def close_connection(self):
        """Close the VISA session.

        """
        self._driver.close()
        self._driver = None

    def reopen_connection(self):
        """Close and re-open a suspicious connection.

        A VISA clear command is issued after re-opening the connection to make
        sure the instrument queues do not keep corrupted data.

        """
        self.close_connection()
        self.open_connection()
        self._driver.clear()
        # Make sure the clear command completed before sending more commands.
        sleep(0.3)

    # --- Pyvisa wrappers

    @property
    def timeout(self):
        """The timeout in milliseconds for all resource I/O operations.

        None is mapped to VI_TMO_INFINITE.
        A value less than 1 is mapped to VI_TMO_IMMEDIATE.
        """
        return self._driver.timeout

    @timeout.setter
    def timeout(self, timeout):
        self._driver.timeout = timeout
        self._para['timeout'] = timeout

    @timeout.deleter
    def timeout(self):
        del self._driver.timeout
        del self._para.timeout

    @property
    def resource_info(self):
        """See Pyvisa docs.

        """
        return self._driver.resource_info

    @property
    def interface_type(self):
        """See Pyvisa docs.

        """
        return self._driver.interface_type

    def clear(self):
        """Clears this resource
        """
        self._driver.clear()

    def install_handler(self, event_type, handler, user_handle=None):
        """See Pyvisa docs.

        """
        return self._driver.install_handlers(event_type, handler, user_handle)

    def uninstall_handler(self, event_type, handler, user_handle=None):
        """See Pyvisa docs.

        """
        self._driver.uninstall_handler(self, event_type, handler, user_handle)


class VisaMessageInstrument(BaseVisaInstrument):
    """Base class for driver communicating using VISA through text based
    messages.

    This covers among others GPIB, USB, TCPIP in INSTR mode, TCPIP in SOCKET
    mode.

    """
    #: Status byte of the instrument.
    status_byte = Register(getter=True, names=[None]*8)

    def default_get_iproperty(self, iprop, cmd, *args, **kwargs):
        """Query the value using the provided command.

        The command is formatted using the provided args and kwargs before
        being passed on to the instrument.

        """
        return self._driver.query(cmd.format(*args, **kwargs))

    def default_set_iproperty(self, iprop, cmd, *args, **kwargs):
        """Set the iproperty value of the instrument.

        The command is formatted using the provided args and kwargs before
        being passed on to the instrument.

        """
        self._driver.write(cmd.format(*args, **kwargs))

    # --- Pyvisa wrappers -----------------------------------------------------
    @property
    def encoding(self):
        """Encoding used for read and write operations.
        """
        return self._driver._encoding

    @encoding.setter
    def encoding(self, encoding):
        self._driver._encoding = encoding
        self._para['encoding'] = encoding

    @property
    def read_termination(self):
        """Read termination character.
        """
        return self._driver._read_termination

    @read_termination.setter
    def read_termination(self, value):
        self._driver._read_termination = value
        self._para['read_termination'] = value

    @property
    def write_termination(self):
        """Writer termination character.
        """
        return self._driver._write_termination

    @write_termination.setter
    def write_termination(self, value):
        self._driver._write_termination = value
        self._para['write_termination'] = value

    def write_raw(self, message):
        """See Pyvisa docs.

        """
        return self._driver.write_raw(message)

    def write(self, message, termination=None, encoding=None):
        """See Pyvisa docs.

        """
        return self._driver.write(message, termination, encoding)

    def write_ascii_values(self, message, values, converter='f', separator=',',
                           termination=None, encoding=None):
        """See Pyvisa docs.

        """
        return self._driver.write_ascii_values(message, values, converter,
                                               separator, termination, encoding
                                               )

    def write_binary_values(self, message, values, datatype='f',
                            is_big_endian=False, termination=None,
                            encoding=None):
        """See Pyvisa docs.

        """
        return self._driver.write_binary_values(message, values, datatype,
                                                is_big_endian, termination,
                                                encoding)

    def write_values(self, message, values, termination=None, encoding=None):
        """See Pyvisa docs.

        """
        return self._driver.write_values(message, values, termination,
                                         encoding)

    def read_raw(self, size=None):
        """See Pyvisa docs.

        """
        return self._driver.read_raw(size)

    def read(self, termination=None, encoding=None):
        """See Pyvisa docs.

        """
        return self._driver.read(termination, encoding)

    def read_values(self, fmt=None, container=list):
        """See Pyvisa docs.

        """
        return self._driver.read_values(fmt, container)

    def query(self, message, delay=None):
        """See Pyvisa docs.

        """
        return self._driver.query(message, delay)

    def query_values(self, message, delay=None):
        """See Pyvisa docs.

        """
        return self._driver.query_values(message, delay)

    def query_ascii_values(self, message, converter='f', separator=',',
                           container=list, delay=None):
        """See Pyvisa docs.

        """
        return self._driver.query_ascii_values(message, converter, separator,
                                               container, delay)

    def query_binary_values(self, message, datatype='f', is_big_endian=False,
                            container=list, delay=None, header_fmt='ieee'):
        """See Pyvisa docs.

        """
        return self._driver.query_binary_values(message, datatype,
                                                is_big_endian, container,
                                                delay, header_fmt)

    def assert_trigger(self):
        """Sends a software trigger to the device.

        """
        self._driver.assert_trigger()

    def _get_status_byte(self, iprop):
        return self._driver.read_stb()


class VisaRegisterInstrument(BaseVisaInstrument):
    """Base class for driver based on VISA and a binary registry.

    This covers among others PXI, ...

    """
    def read_memory(self, space, offset, width, extended=False):
        """See Pyvisa docs.

        """
        return self._driver.read_memory(space, offset, width, extended)

    def write_memory(self, space, offset, data, width, extended=False):
        """See Pyvisa docs.

        """
        return self._driver.write_memory(space, offset, data, width, extended)

    def move_in(self, space, offset, length, width, extended=False):
        """See Pyvisa docs.

        """
        return self._driver.move_in(space, offset, length, width, extended)

    def move_out(self, space, offset, length, data, width, extended=False):
        """See Pyvisa docs.

        """
        return self._driver.move_out(space, offset, length, data, width,
                                     extended)

DRIVER_TYPES = {'VisaMessage': VisaMessageInstrument,
                'VisaRegister': VisaRegisterInstrument}
