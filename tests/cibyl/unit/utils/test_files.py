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
import os
import os.path
from unittest import TestCase
from unittest.mock import Mock, call

from cibyl.utils.files import (FileSearch, get_file_name_from_path,
                               get_first_available_file)


class TestFileSearch(TestCase):
    """Tests for :class:`FileSearch`.
    """

    def test_list_files_in_directory(self):
        """Checks that all files in a directory can be listed.
        """
        directory = 'path/to/dir'

        file1 = 'file1.txt'
        file2 = 'file2.txt'

        os.listdir = Mock()
        os.listdir.return_value = [file1, file2]

        search = FileSearch(directory)

        self.assertEqual(
            [
                f'{directory}/{file1}',
                f'{directory}/{file2}'
            ],
            search.get()
        )

        os.listdir.assert_called_once_with(directory)

    def test_filter_by_extension(self):
        """Checks that files can be filtered by an extension.
        """
        directory = 'path/to/dir'

        file1 = 'file1.py'
        file2 = 'file2.txt'

        os.listdir = Mock()
        os.listdir.return_value = [file1, file2]

        search = FileSearch(directory) \
            .with_extension('.py')

        self.assertEqual(
            [
                f'{directory}/{file1}'
            ],
            search.get()
        )

        os.listdir.assert_called_once_with(directory)

    def test_filter_by_extensions(self):
        """Checks that files can be filtered by more than one extension.
        """
        directory = 'path/to/dir'

        file1 = 'file1.py'
        file2 = 'file2.txt'

        os.listdir = Mock()
        os.listdir.return_value = [file1, file2]

        search = FileSearch(directory) \
            .with_extension('.py') \
            .with_extension('.txt')

        self.assertEqual(
            [
                f'{directory}/{file1}',
                f'{directory}/{file2}'
            ],
            search.get()
        )

        os.listdir.assert_called_once_with(directory)

    def test_recursive(self):
        """Checks that it is possible to recurse over subdirectories
        to find more files.
        """

        def listdir(__dir):
            if __dir == directory:
                return [file1, file2, subdirectory]
            elif __dir == f'{directory}/{subdirectory}':
                return [file3, file4]

            raise NotImplementedError

        def isdir(__dir):
            if __dir == f'{directory}/{subdirectory}':
                return True

            return False

        directory = 'path/to/dir'

        file1 = 'file1.py'
        file2 = 'file2.txt'

        subdirectory = 'subdir'

        file3 = 'file3.md'
        file4 = 'file4.rst'

        os.listdir = Mock()
        os.listdir.side_effect = listdir

        os.path.isdir = Mock()
        os.path.isdir.side_effect = isdir

        search = FileSearch(directory) \
            .with_recursion()

        self.assertEqual(
            [
                f'{directory}/{file1}',
                f'{directory}/{file2}',
                f'{directory}/{subdirectory}/{file3}',
                f'{directory}/{subdirectory}/{file4}',
            ],
            search.get()
        )

        os.listdir.assert_has_calls(
            [
                call(directory),
                call(f'{directory}/{subdirectory}')
            ]
        )

    def test_recursion_and_extensions(self):
        """Checks that it is possible to combine the two filters.
        """

        def listdir(__dir):
            if __dir == directory:
                return [file1, file2, subdirectory]
            elif __dir == f'{directory}/{subdirectory}':
                return [file3, file4]

            raise NotImplementedError

        def isdir(__dir):
            if __dir == f'{directory}/{subdirectory}':
                return True

            return False

        directory = 'path/to/dir'

        file1 = 'file1.py'
        file2 = 'file2.txt'

        subdirectory = 'subdir'

        file3 = 'file3.md'
        file4 = 'file4.rst'

        os.listdir = Mock()
        os.listdir.side_effect = listdir

        os.path.isdir = Mock()
        os.path.isdir.side_effect = isdir

        search = FileSearch(directory) \
            .with_recursion() \
            .with_extension('.md')

        self.assertEqual(
            [
                f'{directory}/{subdirectory}/{file3}'
            ],
            search.get()
        )

        os.listdir.assert_has_calls(
            [
                call(directory),
                call(f'{directory}/{subdirectory}')
            ]
        )


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
