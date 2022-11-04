"""
#    Copyright 2022 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
from unittest import TestCase

from cibyl.exceptions import CibylException
from cibyl.exceptions.wrapper import wrap_exception


class TestWrapException(TestCase):
    """Checks for :func:'wrap_exception'.
    """

    class CustomError(Exception):
        """Type to be raised as the cause for the error.
        """

    class WrapperError(CibylException):
        """Type to be caught from a wrapper function.
        """

    def test_wraps_error(self):
        """Checks that errors coming out of the function get wrapped around
        the custom type.
        """
        msg = 'hello error!'

        @wrap_exception(TestWrapException.WrapperError, message=msg)
        def function():
            raise TestWrapException.CustomError

        try:
            function()
        except Exception as ex:
            self.assertIsInstance(ex, TestWrapException.WrapperError)
            self.assertIsInstance(ex.__cause__, TestWrapException.CustomError)

            self.assertEqual(msg, str(ex))
