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
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from tripleo.utils.types import URL, Dir, File


class TestDir(TestCase):
    """Tests for :class:`Dir`.
    """

    def test_error_if_dir_does_not_exist(self):
        """Checks that an error is thrown if the path does not point to an
        existing directory.
        """
        path = Mock(spec=Path)
        path.is_dir = Mock()
        path.is_dir.return_value = False

        with self.assertRaises(ValueError):
            Dir(path)

        path.is_dir.assert_called_once()

    def test_checks_if_dir_is_empty(self):
        """Checks that the class is capable of knowing if a directory is
        empty or not.
        """
        path = Mock(spec=Path)
        path.is_dir = Mock()
        path.is_dir.return_value = True

        path.iterdir = Mock()
        path.iterdir.return_value = []

        directory = Dir(path)

        self.assertTrue(directory.is_empty())

        path.iterdir.assert_called_once()

    def test_as_path(self):
        """Checks that the type can be converted into a path.
        """
        path = Mock(spec=Path)
        path.is_dir = Mock()
        path.is_dir.return_value = True

        directory = Dir(path)

        self.assertEqual(path, directory.as_path())

    def test_as_str(self):
        """Checks that the type can be converted into a string.
        """
        path = Mock(spec=Path)
        path.is_dir = Mock()
        path.is_dir.return_value = True

        directory = Dir(path)

        self.assertEqual(str(path), directory.as_str())

    def test_str(self):
        """Checks that the type can be converted into a string through __str__.
        """
        path = Mock(spec=Path)
        path.is_dir = Mock()
        path.is_dir.return_value = True

        directory = Dir(path)

        self.assertEqual(str(path), str(directory))

    def test_as_absolute(self):
        """Checks that the type can be transformed into an absolute path.
        """
        absolute = Mock()

        path = Mock(spec=Path)
        path.is_dir = Mock()
        path.is_dir.return_value = True

        path.absolute = Mock()
        path.absolute.return_value = absolute

        directory = Dir(path)

        self.assertEqual(str(absolute), directory.absolute())


class TestFile(TestCase):
    """Tests for :class:`File`.
    """

    def test_error_if_file_does_not_exist(self):
        """Checks that an error is thrown if the path does not point to an
        existing file.
        """
        path = Mock(spec=Path)
        path.is_file = Mock()
        path.is_file.return_value = False

        with self.assertRaises(ValueError):
            File(path)

        path.is_file.assert_called_once()

    def test_as_path(self):
        """Checks that the type can be converted into a path.
        """
        path = Mock(spec=Path)
        path.is_file = Mock()
        path.is_file.return_value = True

        file = File(path)

        self.assertEqual(path, file.as_path())

    def test_as_str(self):
        """Checks that the type can be converted into a string.
        """
        path = Mock(spec=Path)
        path.is_file = Mock()
        path.is_file.return_value = True

        file = File(path)

        self.assertEqual(str(path), file.as_str())

    def test_str(self):
        """Checks that the type can be converted into a string through __str__.
        """
        path = Mock(spec=Path)
        path.is_file = Mock()
        path.is_file.return_value = True

        file = File(path)

        self.assertEqual(str(path), str(file))

    def test_as_absolute(self):
        """Checks that the type can be transformed into an absolute path.
        """
        absolute = Mock()

        path = Mock(spec=Path)
        path.is_file = Mock()
        path.is_file.return_value = True

        path.absolute = Mock()
        path.absolute.return_value = absolute

        file = File(path)

        self.assertEqual(str(absolute), file.absolute())


class TestURL(TestCase):
    """Tests for :class:`URL`.
    """

    @patch('tripleo.utils.types.is_url')
    def test_new_on_valid_url(self, check_mock: Mock):
        """Checks that if the string is a URL, the string is created.
        """
        string = 'some-string-that-is-a-url'

        check_mock.return_value = True

        self.assertEqual(string, URL(string))

        check_mock.assert_called_once_with(string)

    @patch('tripleo.utils.types.is_url')
    def test_error_on_invalid_url(self, check_mock: Mock):
        """Checks that if the string is not a URL, an error is thrown.
        """
        string = 'some-string-that-is-no-url'

        check_mock.return_value = False

        with self.assertRaises(ValueError):
            URL(string)

        check_mock.assert_called_once_with(string)

    @patch('tripleo.utils.types.is_url')
    def test_trims_string(self, check_mock: Mock):
        """Checks that before verifying the string, it is trimmed first.
        """
        string = 'some-string-that-is-a-url'
        broken_string = f'{string}  '

        check_mock.return_value = True

        self.assertEqual(string, URL(broken_string))

        check_mock.assert_called_once_with(string)
