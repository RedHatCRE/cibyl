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

from tripleo.utils.git.gitpython import Repository


class TestRepository(TestCase):
    """Tests for :class:`Repository`.
    """

    def test_with_keyword(self):
        """Checks that the class is compatible with the 'with' keyword.
        """
        handler = Mock()
        handler.close = Mock()

        with Repository(handler):
            pass

        handler.close.assert_called_once()

    def test_is_closeable(self):
        """Checks that the class implements the closeable interface.
        """
        handler = Mock()
        handler.close = Mock()

        repo = Repository(handler)

        repo.close()

        handler.close.assert_called_once()
