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

from cibyl.utils.files import get_file_name_from_path, get_first_available_file


class TestGetFirstAvailableFile(TestCase):
    """Test cases for the 'get_first_available_file' function.
    """

    def test_no_file_found(self):
        """Checks that 'None' is returned when no provided file exists.
        """
        self.assertIsNone(
            get_first_available_file(
                ['path/to/some/file'],
                lambda file: False  # File will never be available
            )
        )

    def test_will_report_found_file(self):
        """Checks that, when a file is available, the function will notice and
        return it.
        """
        expected_file = 'path/to/expected/file'

        self.assertEqual(
            get_first_available_file(
                [
                    'path/to/fake/file/1',
                    expected_file,
                    'path/to/fake/file/2'
                ],
                lambda file: file == expected_file
            ),
            expected_file
        )


class TestGetFileNameFromPath(TestCase):
    """Test cases for the 'get_file_name_from_path' function.
    """
    def test_file_name(self):
        """Checks that the file name is extracted from a path and the extension
        is stripped."""
        file_path = 'path/to/expected/file.txt'
        file_name = get_file_name_from_path(file_path)
        self.assertEqual(file_name, "file")

    def test_file_name_abs_path(self):
        """Checks that the file name is extracted from a path and the extension
        is stripped."""
        file_path = '/path/to/expected/file.txt'
        file_name = get_file_name_from_path(file_path)
        self.assertEqual(file_name, "file")

    def test_file_name_no_extension(self):
        """Checks that the file name is extracted from a path with no
        extension."""
        file_path = 'path/to/expected/file'
        file_name = get_file_name_from_path(file_path)
        self.assertEqual(file_name, "file")

    def test_file_name_no_leading_path(self):
        """Checks that the file name is extracted from a path with no parent
        folders and the extension is stripped."""
        file_path = 'file.txt'
        file_name = get_file_name_from_path(file_path)
        self.assertEqual(file_name, "file")

    def test_file_name_windows_path(self):
        """Checks that the file name is extracted from a path and the extension
        is stripped."""
        file_path = r'C:\path\expected\file.txt'
        file_name = get_file_name_from_path(file_path)
        self.assertEqual(file_name, "file")

    def test_file_name_windows_path_no_extension(self):
        """Checks that the file name is extracted from a path with no
        extension."""
        file_path = 'C:\\path\\expected\\file'
        file_name = get_file_name_from_path(file_path)
        self.assertEqual(file_name, "file")
