# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" Collection of useful functions.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from functools import wraps
import logging


def secure_communication(max_iter=3):
    """Decorator making sure that a communication error cannot simply be
    resolved by attempting again to send a message.

    Parameters
    ----------
    max_iter : int, optionnal
        Maximum number of attempt to perform before propagating the exception.

    """
    def decorator(method):

        @wraps(method)
        def wrapper(self, *args, **kwargs):

            i = 0
            # Try at most `max_iter` times to excute method
            while i < max_iter + 1:
                self.lock.acquire()
                try:
                    return method(self, *args, **kwargs)

                # Catch all the exception specified by the driver
                except self.secure_com_exceptions as e:
                    if i == max_iter:
                        raise
                    else:
                        logger = logging.getLogger(__name__)
                        logger.error(e)
                        self.reopen_connection()
                        i += 1
                finally:
                    self.lock.release()

        wrapper.__wrapped__ = method
        return wrapper

    return decorator
