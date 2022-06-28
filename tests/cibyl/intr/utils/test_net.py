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
from unittest import TestCase, skip

from cibyl.utils.net import download_into_memory
from tests.cibyl.e2e.containers.httpd import HTTPDContainer


class TestDownloadIntoMemory(TestCase):
    """Tests for :func:`download_into_memory`.
    """

    @skip
    def test_provides_contents(self):
        """Checks that the data read from the remote matches with the
        original file.
        """
        with HTTPDContainer() as httpd:
            file_url = f'{httpd.url}/jenkins.yaml'
            file_path = 'tests/cibyl/e2e/data/images/httpd/public/jenkins.yaml'

            with open(file_path, encoding='utf-8') as file:
                self.assertEqual(
                    file.read(),
                    download_into_memory(file_url)
                )
