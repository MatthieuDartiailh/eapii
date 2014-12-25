.. _installation:

============
Installation
============

.. contents::

Installing Eapii is straightforward. It is a pure python package and can be
installed using pip ::

$ pip install eapii

It has two single manadatory dependencies : `future`_ for Python2/3
compatibility and `Pint`_ for unit handling. If you need to communicate with
instruments through the VISA protocol, you will also need to install `PyVISA`_
(> 1.6).

In order to run the testsuite you will also need py.test and if you want to
build the docs you will need sphinx, the sphinx extension napoleon and the
sphinx Read the docs theme. All can be installed through pip using the
following commands :

    >>> pip install py.test
    >>> pip install sphinx
    >>> pip install spinxcontrib.napoleon
    >>> pip install sphinx_rtd_theme

.. _future: http://python-future.org/
.. _Pint: http://pint.readthedocs.org/en
.. _PyVISA: http://pyvisa.readthedocs.org/en/1.6/index.html)


Testing your installation
-------------------------

To test your installation open a python interpreter and ask Eapii to list all
the drivers it knows :

    >>> from eapii.explore import list_drivers, print_loading_errors
    >>> list_drivers()
    >>> print_loading_errors()

The last command will have no output if everything went well.

If you encounter any problem, take a look at the :ref:`faqs`. If everything
fails, feel free to open an issue in our `issue_tracker`_.

.. _issue_tracker: http://github.com/MatthieuDartiailh/eapii/issues


Using the development version
-----------------------------

Tou can install the development version directly from `Github`_ ::

    $ pip install https://github.com/MatthieuDartiailh/eapii/zipball/master

.. _Github: http://github.com
