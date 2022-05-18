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
from unittest.mock import Mock, patch

from cibyl.outputs.cli.ci.system.common.jobs import (get_plugin_section,
                                                     has_plugin_section)


class TestHasPluginSection(TestCase):
    """Tests for :func:`has_plugin_section`
    """

    def test_attributes_is_none(self):
        """Checks result is false if the plugins attributes of a job is none.
        """
        job = Mock()
        job.plugin_attributes = None

        self.assertFalse(has_plugin_section(job))

    def test_attributes_is_empty(self):
        """Checks result is false if the plugins attributes of a job is empty.
        """
        job = Mock()
        job.plugin_attributes = {}

        self.assertFalse(has_plugin_section(job))

    def test_attributes_is_filled(self):
        """Checks result is true if the plugins attributes of a job is
        filled with data.
        """
        job = Mock()
        job.plugin_attributes = {
            'plugin1': {}
        }

        self.assertTrue(has_plugin_section(job))


class TestGetPluginSection(TestCase):
    """Tests for :func:`get_plugin_section`.
    """

    @patch('cibyl.outputs.cli.ci.system.common.jobs.has_plugin_section')
    def test_error_if_no_attributes(self, check_mock):
        """Checks that an error is thrown if the job has no plugins to
        describe.
        """
        check_mock.return_value = False

        printer = Mock()
        job = Mock()

        with self.assertRaises(ValueError):
            get_plugin_section(printer, job)
