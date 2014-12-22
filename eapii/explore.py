# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
"""Utility functions to collect the defined driver types and driver.

Drivers and driver types are looked for in all modules presents in clib and
visa. Drivers should be declared in a module variable DRIVERS and driver types
in one named DRIVER_TYPES. Both should be dictionary of name: class. Driver
types are generic driver not meant to be instantiated but describing a
communication protocole.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
import os
import logging
from importlib import import_module


def list_drivers(filters=None, force=False):
    """List the drivers known to Eapii.

    Parameters
    ----------
    filters : list(callable), optional
        Filter functions receiving the dict of all known drivers and which
        should remove in place some entries.

    force : bool, optional
        Flag indicating whether or not all packages should be explored again.

    """
    if force or not _DRIVERS:
        _refresh_drivers()

    d = _DRIVERS.copy()
    if filters:
        for f in filters:
            f(d)
    return d.keys()


def list_driver_types(force=False):
    """List the driver types known to Eapii.

    Parameters
    ----------
    force : bool, optional
        Flag indicating whether or not all packages should be explored again.

    """
    if force or not _DRIVER_TYPES:
        _refresh_drivers()

    d = _DRIVER_TYPES.copy()
    return d.keys()


def get_driver(name):
    """Retrieve a driver using its name.

    Parameters
    ----------
    name : unicode
        Name of the driver to retrive.

    Returns
    -------
    driver : type
        Assocaiated with the given name

    Raises
    ------
    KeyError : if the name is not present in the list of drivers.

    """
    if not _DRIVERS:
        _refresh_drivers()

    return _DRIVERS[name]


def get_driver_type(name):
    """Retrieve a driver type using its name.

    Parameters
    ----------
    name : unicode
        Name of the driver to retrive.

    Returns
    -------
    driver : type
        Assocaiated with the given name

    Raises
    ------
    KeyError : if the name is not present in the list of driver types.

    """
    if not _DRIVER_TYPES:
        _refresh_drivers()

    return _DRIVER_TYPES[name]


def loading_errors():
    """Access the errors that occured when collecting the drivers.

    """
    return _ISSUES.copy()


def print_loading_errors():
    """Pretty printing of the errors that occured when collecting the drivers.

    """
    for i, m in _ISSUES.items():
        mess = 'The following issue happened when importing {}: {}'
        print(mess.format(i, m))

# =============================================================================
# --- Private exploration functions.
# =============================================================================

_PACKAGE_PATH = os.path.join(os.path.dirname(__file__))

_MODULE_ANCHOR = 'eapii'

_DRIVERS = {}

_DRIVER_TYPES = {}

_ISSUES = {}

_TOPLEVELS = ('visa', 'clib')


def _refresh_drivers():
    """ Refresh the known driver types and drivers.

    """
    failed = {}
    driver_types = {}
    driver_packages = list(_TOPLEVELS)
    drivers = {}

    # Explore packages
    while driver_packages:
        pack = driver_packages.pop(0)
        pack_path = os.path.join(_PACKAGE_PATH, *pack.split('.'))

        modules, packs = _explore_package(pack, pack_path, failed)
        driver_packages.extend(packs)

        _explore_modules_for_drivers(modules, driver_types,
                                     drivers, failed, prefix=pack)

    global _DRIVERS, _DRIVER_TYPES, _ISSUES
    _DRIVERS = drivers
    _DRIVER_TYPES = driver_types
    _ISSUES = failed


def _explore_modules_for_drivers(modules, types, drivers, failed, prefix):
    """ Explore a list of modules.

    Parameters
    ----------
    modules : list
        The list of modules to explore

    types : dict
        A dict in which discovered types will be stored.

    packages : list
        A list in which discovered packages will be stored.

    drivers : dict
        A dict in which discovered drivers will be stored.

    failed : list
        A list in which failed imports will be stored.

    """
    for mod in modules:
        try:
            m = import_module('.' + mod, _MODULE_ANCHOR)
        except Exception as e:
            log = logging.getLogger(__name__)
            mess = 'Failed to import mod {} : {}'.format(mod, e)
            log.error(mess)
            failed[mod] = mess
            continue

        if hasattr(m, 'DRIVER_TYPES'):
            types.update(m.DRIVER_TYPES)

        if hasattr(m, 'DRIVERS'):
            drivers.update(m.DRIVERS)


def _explore_package(pack, pack_path, failed):
    """ Explore a package

    Parameters
    ----------
    pack : str
        The package name relative to "eapii". (ex : visa)

    pack_path : unicode
        Path of the package to explore

    failed : dict
        A dict in which failed imports will be stored.

    Returns
    -------
    modules : list
        List of string indicating modules which can be imported

    """
    if not os.path.isdir(pack_path):
        log = logging.getLogger(__name__)
        mess = '{} is not a valid directory.({})'.format(pack,
                                                         pack_path)
        log.error(mess)
        failed[pack] = mess
        return []

    i = len('.py')
    modules = sorted(pack + '.' + m[:-i] for m in os.listdir(pack_path)
                     if (os.path.isfile(os.path.join(pack_path, m))
                         and m.endswith('.py')))

    packs = sorted(pack + '.' + p for p in os.listdir(pack_path)
                   if os.path.isdir(os.path.join(pack_path, p)))

    try:
        modules.remove(pack + '.__init__')
    except ValueError:
        log = logging.getLogger(__name__)
        mess = '{} is not a valid Python package (miss __init__.py).'
        log.error(mess.format(pack))
        failed[pack] = mess
        return []

    return modules, packs
