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
from unittest.mock import Mock

from tripleo.utils.paths import resolve_home


class TestResolveHome(TestCase):
    """Tests for :func:`resolve_home`.
    """

    def test_resolves_home_shortcut(self):
        """Checks that the function is capable of expanding the '~'
        shortcut.
        """
        home = '/home'

        path = Mock(spec=Path)

        path.home = Mock()
        path.home.return_value = home

        path.__str__ = Mock()
        path.__str__.return_value = '~/path/to/dir'

        result = resolve_home(path)

        self.assertEqual('/home/path/to/dir', str(result))
