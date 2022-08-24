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
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest import TestCase, skip

from tripleo.utils.fs import Dir, File


class TestDir(TestCase):
    """Tests for :class:`Dir`.
    """

    def test_check_exists(self):
        """Check that an error is thrown if the directory does not exist.
        """
        directory = Dir('some/made/up/path')

        with self.assertRaises(IOError):
            directory.check_exists()

    def test_exists(self):
        """Checks that this tells that the path points to a folder which
        exists.
        """
        with TemporaryDirectory() as path:
            directory = Dir(path)

            self.assertTrue(directory.exists())

    def test_not_exists(self):
        """Checks that it can tell if the directory exists.
        """
        directory = Dir('some/made/up/path')

        self.assertFalse(directory.exists())

    def test_not_directory(self):
        """Checks that it can tell if a path is not a directory.
        """
        with NamedTemporaryFile() as buffer:
            directory = Dir(buffer.name)

            self.assertFalse(directory.exists())

    def test_dir_is_empty(self):
        """Checks that this can tell whether the directory has files in it
        or not.
        """
        with TemporaryDirectory() as folder:
            directory = Dir(folder)

            self.assertTrue(directory.is_empty())

            with NamedTemporaryFile(dir=directory):
                self.assertFalse(directory.is_empty())

    def test_cd(self):
        """Checks that a path to a subdirectory is created as expected.
        """
        subfolder = 'folder'

        with TemporaryDirectory() as folder:
            directory = Dir(folder)

            self.assertEqual(
                f'{directory}/{subfolder}',
                directory.cd(subfolder)
            )

    def test_mkdir_error(self):
        """Checks that an error is raised if the directory's parents do not
        exist.
        """
        directory = Dir('path/to/some/dir')

        with self.assertRaises(FileNotFoundError):
            directory.mkdir(recursive=False)

    def test_simple_mkdir(self):
        """Checks that a folder can be created under a parent directory.
        """
        with TemporaryDirectory() as folder:
            directory = Dir(f'{folder}/dir')

            self.assertFalse(directory.exists())

            directory.mkdir(recursive=False)

            self.assertTrue(directory.exists())

    def test_recursive_mkdir(self):
        """Checks that all the folders leading to a directory can be
        created.
        """
        with TemporaryDirectory() as folder:
            directory = Dir(f'{folder}/dir/subdir')

            self.assertFalse(directory.exists())

            directory.mkdir(recursive=True)

            self.assertTrue(directory.exists())

    @skip(reason='Will fail on CI')
    def test_rm(self):
        """Checks that it is possible to delete the folder and everything
        inside.
        """
        with TemporaryDirectory() as folder:
            directory = Dir(folder)

            self.assertTrue(directory.exists())

            directory.rm()

            self.assertFalse(directory.exists())

    def test_as_path(self):
        """Checks that the type can be converted into a path.
        """
        path = Path('path/to/dir')

        directory = Dir(path)

        self.assertEqual(path, directory.as_path())

    def test_str(self):
        """Checks that the type can be converted into a string through __str__.
        """
        path = 'path/to/dir'

        directory = Dir(path)

        self.assertEqual(path, str(directory))


class TestFile(TestCase):
    """Tests for :class:`File`.
    """

    def test_check_exists(self):
        """Checks that an error is thrown if the file does not exist.
        """
        file = File('some/path/to/a/file')

        with self.assertRaises(IOError):
            file.check_exists()

    def test_exists(self):
        """Checks that this is able to tell whether a file exists on the
        filesystem or not.
        """
        with NamedTemporaryFile() as buffer:
            file = File(buffer.name)

            self.assertTrue(file.exists())

    def test_not_file(self):
        """Checks that it can tell if a path is a file or not.
        """
        with TemporaryDirectory() as folder:
            file = File(folder)

            self.assertFalse(file.exists())

    def test_as_path(self):
        """Checks that the type can be converted into a path.
        """
        path = Path('path/to/file')

        file = File(path)

        self.assertEqual(path, file.as_path())

    def test_str(self):
        """Checks that the type can be converted into a string through __str__.
        """
        path = 'path/to/file'

        file = File(path)

        self.assertEqual(path, str(file))
