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
from tempfile import TemporaryDirectory, NamedTemporaryFile
from unittest import TestCase

from cibyl.sources.zuuld.tools.yaml import YAMLSearch
from kernel.tools.fs import Dir


class TestYAMLSearch(TestCase):
    """Tests for :class:`YAMLSearch`.
    """

    def test_finds_files(self):
        """Checks that the class is able to find the desired files.
        """
        with TemporaryDirectory() as folder:
            directory = Dir(folder)

            subdirectory = directory.cd('subdir')
            subdirectory.mkdir()

            with NamedTemporaryFile(suffix='.yaml', dir=directory):
                with NamedTemporaryFile(suffix='.yml', dir=subdirectory):
                    search = YAMLSearch()

                    result = list(search.search(directory))

                    self.assertEqual(2, len(result))
                    self.assertTrue(result[0].endswith('.yaml'))
                    self.assertTrue(result[1].endswith('.yml'))
