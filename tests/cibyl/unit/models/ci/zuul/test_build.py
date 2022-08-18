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

    def test_attributes(self):
        """Checks that the model has the desired attributes.
        """
        project = 'project'
        pipeline = 'pipline'
        suites = [Mock(), Mock()]
        uuid = 'uuid'
        status = 'STATUS'
        duration = 1

        data = Build.Data(uuid, project, pipeline, status, duration)
        build = Build(data, suites)

        self.assertEqual(uuid, build.build_id.value)
        self.assertEqual(project, build.project.value)
        self.assertEqual(pipeline, build.pipeline.value)
        self.assertEqual(status, build.status.value)
        self.assertEqual(duration, build.duration.value)
        self.assertEqual(suites, build.suites.value)

    def test_equality_by_type(self):
        """Checks that a build is not equal to something not of its type.
        """
        data = Build.Data('uuid', 'project', 'pipeline', 'status', 0)
        build = Build(data)
        other = Mock()

        self.assertNotEqual(other, build)

    def test_equality_by_reference(self):
        """Checks that a build is equal to itself.
        """
        data = Build.Data('uuid', 'project', 'pipeline', 'status', 0)
        build = Build(data)

        self.assertEqual(build, build)

    def test_equality_by_contents(self):
        """Checks that a build equals another whose contents are the same.
        """
        data = Build.Data('uuid', 'project', 'pipeline', 'status', 0)
        build1 = Build(data)
        build2 = Build(data)

        self.assertEqual(build2, build1)

    def test_adds_suite(self):
        """Checks that the build will add a suite that it does not already
        hold.
        """
        suite = Mock()

        data = Mock()

        build = Build(data)
        build.add_suite(suite)

        self.assertEqual(1, len(build.suites))
        self.assertEqual(suite, build.suites[0])

    def test_ignores_suite(self):
        """Checks that the build will not add a suite it already contains.
        """
        suite = Mock()

        data = Mock()

        build = Build(data, suites=[suite])
        build.add_suite(suite)

        self.assertEqual(1, len(build.suites))
        self.assertEqual(suite, build.suites[0])

    def test_none_on_unknown_suite(self):
        """Checks that none is returned if an unknown suite is requested.
        """
        data = Mock()

        build = Build(data)

        self.assertIsNone(build.get_suite('some_suite'))

    def test_gets_suite(self):
        """Checks that the build can fetch a suite within it by name.
        """
        name = 'name'

        suite = Mock()
        suite.name = Mock()
        suite.name.value = name

        data = Mock()

        build = Build(data, suites=[suite])

        self.assertEqual(suite, build.get_suite(name))

    def test_merge_suites(self):
        """Checks that the suites from a build are added to the other on
        merge.
        """
        suite = Mock()

        data = Mock()

        build1 = Build(data)
        build2 = Build(data, suites=[suite])

        build1.merge(build2)

        self.assertEqual(1, len(build1.suites))
        self.assertEqual(suite, build1.suites[0])
