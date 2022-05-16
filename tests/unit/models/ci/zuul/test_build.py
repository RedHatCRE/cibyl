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

from cibyl.models.ci.zuul.build import Build


class TestBuild(TestCase):
    """Tests for :class:`Build`.
    """

    def test_equality_by_type(self):
        """Checks that a build is not equal to something not of its type.
        """
        info = Build.Info('project', 'pipeline', 'uuid', 'status', 0)
        build = Build(info)
        other = Mock()

        self.assertNotEqual(other, build)

    def test_equality_by_reference(self):
        """Checks that a build is equal to itself.
        """
        info = Build.Info('project', 'pipeline', 'uuid', 'status', 0)
        build = Build(info)

        self.assertEqual(build, build)

    def test_equality_by_contents(self):
        """Checks that a build equals another whose contents are the same.
        """
        info = Build.Info('project', 'pipeline', 'uuid', 'status', 0)
        build1 = Build(info)
        build2 = Build(info)

        self.assertEqual(build2, build1)
