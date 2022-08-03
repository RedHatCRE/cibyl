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
from unittest.mock import Mock

from cibyl.sources.zuul.utils.artifacts.manifest import ManifestFile
from cibyl.sources.zuul.utils.builds import get_url_to_build_file


class TestGetURLToBuildFile(TestCase):
    """Tests for :func:`get_url_to_build_file`.
    """

    def test_url_is_well_build(self):
        """Check that the URL is built as expected.
        """
        build = Mock()
        build.log_url = 'http://localhost:8080/'

        file = '/var/log/file.txt'

        result = get_url_to_build_file(build, ManifestFile(file))

        self.assertEqual('http://localhost:8080/var/log/file.txt', result)
