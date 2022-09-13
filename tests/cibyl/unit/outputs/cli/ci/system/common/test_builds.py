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

from cibyl.outputs.cli.ci.system.common.builds import (get_duration_section,
                                                       get_status_section,
                                                       has_duration_section,
                                                       has_status_section)


class TestHasStatusSection(TestCase):
    """Test for :func:`has_status_section`.
    """

    def test_status_is_none(self):
        """Checks result is false if build has no status.
        """
        build = Mock()
        build.status.value = None

        self.assertFalse(has_status_section(build))

    def test_status_has_value(self):
        """Checks result is true if build has status.
        """
        build = Mock()
        build.status.value = 'MOCKED'

        self.assertTrue(has_status_section(build))


class TestGetStatusSection(TestCase):
    """Tests for :func:`get_status_section`.
    """

    @patch('cibyl.outputs.cli.ci.system.common.builds.has_status_section')
    def test_raises_error_if_invalid(self, check_mock):
        """Checks that an error is raised if the build has no status section.
        """
        check_mock.return_value = False

        palette = Mock()
        build = Mock()

        with self.assertRaises(ValueError):
            get_status_section(palette, build)

    @patch('cibyl.outputs.cli.ci.system.common.builds.has_status_section')
    def test_successful_build(self, check_mock):
        """Checks output for a build with a 'success' state.
        """

        def clear_text(text):
            return text

        check_mock.return_value = True

        palette = Mock()
        palette.blue = Mock()
        palette.blue.side_effect = clear_text
        palette.green = Mock()
        palette.green.side_effect = clear_text

        build = Mock()
        build.status.value = 'SUCCESS'

        self.assertEqual(
            'Status: SUCCESS',
            get_status_section(palette, build)
        )

        palette.blue.assert_called_once_with('Status: ')
        palette.green.assert_called_once_with('SUCCESS')

    @patch('cibyl.outputs.cli.ci.system.common.builds.has_status_section')
    def test_failed_build(self, check_mock):
        """Checks output for a build with a 'failure' state.
        """

        def clear_text(text):
            return text

        check_mock.return_value = True

        palette = Mock()
        palette.blue = Mock()
        palette.blue.side_effect = clear_text
        palette.red = Mock()
        palette.red.side_effect = clear_text

        build = Mock()
        build.status.value = 'FAILURE'

        self.assertEqual(
            'Status: FAILURE',
            get_status_section(palette, build)
        )

        palette.blue.assert_called_once_with('Status: ')
        palette.red.assert_called_once_with('FAILURE')

    @patch('cibyl.outputs.cli.ci.system.common.builds.has_status_section')
    def test_unstable_build(self, check_mock):
        """Checks output for a build with a 'unstable' state.
        """

        def clear_text(text):
            return text

        check_mock.return_value = True

        palette = Mock()
        palette.blue = Mock()
        palette.blue.side_effect = clear_text
        palette.yellow = Mock()
        palette.yellow.side_effect = clear_text

        build = Mock()
        build.status.value = 'UNSTABLE'

        self.assertEqual(
            'Status: UNSTABLE',
            get_status_section(palette, build)
        )

        palette.blue.assert_called_once_with('Status: ')
        palette.yellow.assert_called_once_with('UNSTABLE')

    @patch('cibyl.outputs.cli.ci.system.common.builds.has_status_section')
    def test_unknown_status(self, check_mock):
        """Checks output for a build with an unknown state.
        """

        def clear_text(text):
            return text

        check_mock.return_value = True

        palette = Mock()
        palette.blue = Mock()
        palette.blue.side_effect = clear_text
        palette.underline = Mock()
        palette.underline.side_effect = clear_text

        build = Mock()
        build.status.value = '*UNKNOWN*'

        self.assertEqual(
            'Status: *UNKNOWN*',
            get_status_section(palette, build)
        )

        palette.blue.assert_called_once_with('Status: ')
        palette.underline.assert_called_once_with('*UNKNOWN*')


class TestHasDurationSection(TestCase):
    """Tests for :func:`has_duration_section`.
    """

    def test_duration_is_none(self):
        """Checks result when there is no build's duration.
        """
        build = Mock()
        build.duration.value = None

        self.assertFalse(has_duration_section(build))

    def test_has_duration(self):
        """Checks result when build has duration.
        """
        build = Mock()
        build.duration.value = 1

        self.assertTrue(has_duration_section(build))


class TestGetDurationSection(TestCase):
    """Tests for :func:`get_duration_section`.
    """

    @patch('cibyl.outputs.cli.ci.system.common.builds.has_duration_section')
    def test_raises_error_if_invalid(self, check_mock):
        """Checks that an error is raised if the build has no data to fill
        the section with.
        """
        check_mock.return_value = False

        palette = Mock()
        build = Mock()

        with self.assertRaises(ValueError):
            get_duration_section(palette, build)

    @patch('cibyl.outputs.cli.ci.system.common.builds.has_duration_section')
    def test_output_if_valid(self, check_mock):
        """Checks the output if the build has the data.
        """

        def clear_text(text):
            return text

        check_mock.return_value = True

        palette = Mock()
        palette.blue = Mock()
        palette.blue.side_effect = clear_text

        build = Mock()
        build.duration.value = 60000

        self.assertEqual(
            'Duration: 1.00min',
            get_duration_section(palette, build)
        )

        palette.blue.assert_called_once_with('Duration: ')
