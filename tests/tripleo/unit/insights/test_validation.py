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

from tripleo.insights.exceptions import InsightsError, InvalidURL
from tripleo.insights.validation import OutlineValidator, validate_urls


class TestValidateURLs(TestCase):
    """Tests for :func:`validate_urls`.
    """

    @patch('tripleo.insights.validation.is_git')
    def test_returns_nothing_if_valid(self, check_mock: Mock):
        """If the outline is valid, then this will return nothing.
        """
        outline = Mock()

        check_mock.return_value = True

        error = validate_urls(outline)

        self.assertIsNone(error)

    @patch('tripleo.insights.validation.is_git')
    def test_error_when_invalid_url(self, check_mock: Mock):
        """Checks that if a URL in the outline does not point to a Git
        repository, then an error is returned.
        """
        outline = Mock()

        check_mock.return_value = False

        result = validate_urls(outline)

        self.assertIsInstance(result, InvalidURL)


class TestOutlineValidator(TestCase):
    """Tests for :class:`OutlineValidator`.
    """

    def test_valid_outline(self):
        """Checks the result when an outline is valid.
        """
        outline = Mock()
        validation = Mock()
        validation.return_value = None

        validator = OutlineValidator(validations=(validation,))

        self.assertEqual(
            (True, None),
            validator.validate(outline)
        )

        validation.assert_called_once_with(outline)

    def test_invalid_outline(self):
        """Checks the result when an outline is invalid.
        """
        error = InsightsError()

        outline = Mock()
        validation = Mock()
        validation.return_value = error

        validator = OutlineValidator(validations=(validation,))

        self.assertEqual(
            (False, error),
            validator.validate(outline)
        )

        validation.assert_called_once_with(outline)
