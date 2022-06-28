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

from cibyl.exceptions.source import NoSupportedSourcesFound


class TestCibylExceptions(TestCase):
    """Test the behavior of CibylException types."""

    def test_cibyl_no_supported_sources_found_message(self):
        """"""""
        exception = NoSupportedSourcesFound("system", "func")
        expected = "Couldn't find any enabled source for the system "
        expected += "system that implements the function func."
        self.assertEqual(str(exception), expected)
