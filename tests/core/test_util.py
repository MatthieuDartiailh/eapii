# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright 2014 by Eapii Authors, see AUTHORS for more details.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENCE, distributed with this software.
#------------------------------------------------------------------------------
""" Test for utilities functions from eapii.core.util.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from pytest import raises

from eapii.core.util import secure_communication
from eapii.core.errors import InstrIOError
from .testing_tools import Parent


class TestSecureCommDec(object):

    def setup_class(self):
        class SecTest(Parent):

            secure_com_exceptions = (InstrIOError,)

            def __init__(self, max_fail):
                super(SecTest, self).__init__()
                self.max_fail = max_fail
                self.i = 1

            @secure_communication(3)
            def test(self):
                if self.i > self.max_fail:
                    return 'Test'
                else:
                    self.i += 1
                    raise InstrIOError()

        self.test_cls = SecTest

    def test_no_exception(self):
        tester = self.test_cls(0)
        assert tester.test() == 'Test'
        assert tester.ropen_called == 0

    def test_success_after_reconnection(self):
        tester = self.test_cls(1)
        assert tester.test() == 'Test'
        assert tester.ropen_called == 1

    def test_failure(self):
        tester = self.test_cls(5)
        with raises(InstrIOError):
            tester.test()
        assert tester.ropen_called == 3

    def test_wrong_exception(self):
        tester = self.test_cls(1)

        def a():
            raise ValueError()
        tester.test = a
        with raises(ValueError):
            tester.test()
        assert tester.ropen_called == 0
