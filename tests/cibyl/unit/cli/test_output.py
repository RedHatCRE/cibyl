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

from cibyl.cli.output import OutputStyle


class TestFromKey(TestCase):
    """Tests for :func:`OutputStyle.from_key`.
    """

    def test_text_options(self):
        """Checks that the keys for the TEXT output option return that option.
        """
        self.assertEqual(
            OutputStyle.TEXT,
            OutputStyle.from_key('text')
        )

    def test_colorized_options(self):
        """Checks that the keys for the COLORIZED output option return that
        option.
        """
        self.assertEqual(
            OutputStyle.COLORIZED,
            OutputStyle.from_key('colorized')
        )

    def test_json_options(self):
        """Checks that the keys for the JSON output option return that option.
        """
        self.assertEqual(
            OutputStyle.JSON,
            OutputStyle.from_key('json')
        )
