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

from cibyl.models.ci.zuul.project import Project


class TestProject(TestCase):
    """Tests for :class:`Project`.
    """

    def test_not_equal_by_type(self):
        """Checks that if a project is compared with something of another
        type, they will not be equal.
        """
        project = Project('project', 'url')
        other = Mock()

        self.assertNotEqual(other, project)

    def test_not_equal_by_pipelines(self):
        """Checks that two projects are not equal if they do not hold the same
        pipelines.
        """
        name = 'project'

        pipeline1 = Mock()
        pipeline2 = Mock()

        project1 = Project(name, [pipeline1])
        project2 = Project(name, [pipeline2])

        self.assertNotEqual(project2, project1)

    def test_equal_by_content(self):
        """Checks that two projects are the same if they share the same
        contents.
        """
        name = 'project'
        url = 'url'

        project1 = Project(name, url)
        project2 = Project(name, url)

        self.assertEqual(project2, project1)

    def test_merge_project(self):
        """Checks that the pipelines from one project is added to the other
        during a merge.
        """
        name1 = 'pipeline1'
        name2 = 'pipeline2'

        pipeline1 = Mock()
        pipeline1.name = Mock()
        pipeline1.name.value = name1

        pipeline2 = Mock()
        pipeline2.name = Mock()
        pipeline2.name.value = name2

        project1 = Project('project1', 'url1', {name1: pipeline1})
        project2 = Project('project2', 'url2', {name2: pipeline2})

        project1.merge(project2)

        self.assertEqual(
            {
                name1: pipeline1,
                name2: pipeline2
            },
            project1.pipelines.value
        )

    def test_merge_pipeline(self):
        """Checks that a pipeline that already exists on the project gets
        merged instead of overwritten.
        """
        name = 'pipeline'

        pipeline = Mock()
        pipeline.name = Mock()
        pipeline.name.value = name
        pipeline.merge = Mock()

        project = Project('project', 'url', {name: pipeline})

        project.add_pipeline(pipeline)

        self.assertEqual(
            {
                name: pipeline
            },
            project.pipelines.value
        )

        pipeline.merge.assert_called_once_with(pipeline)
