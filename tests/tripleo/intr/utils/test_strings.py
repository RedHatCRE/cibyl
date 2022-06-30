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

from tripleo.utils.strings import is_url


class TestIsURL(TestCase):
    """Tests for :func:`is_url`.
    """

    def test_is_valid_url(self):
        """Checks that the function returns true if the string is a valid URL.
        """
        url = 'http://localhost:8080/path/to/my/file.txt'

        self.assertTrue(is_url(url))

    def test_is_invalid_url(self):
        """Checks that the function returns false if the string is not a
        valid URL.
        """
        url = 'some-string-that-is-no-url'

        self.assertFalse(is_url(url))
