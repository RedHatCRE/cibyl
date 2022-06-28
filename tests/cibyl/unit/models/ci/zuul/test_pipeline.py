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

from cibyl.models.ci.zuul.pipeline import Pipeline


class TestPipeline(TestCase):
    """Tests for :class:`Pipeline`.
    """

    def test_not_equal_by_type(self):
        """Checks that if a pipeline is compared with something of another
        type, they will not be equal.
        """
        pipeline = Pipeline('pipeline')
        other = Mock()

        self.assertNotEqual(other, pipeline)

    def test_not_equal_by_jobs(self):
        """Checks that two pipelines are not equal if they do not hold the
        same jobs.
        """
        name = 'pipeline'

        job1 = Mock()
        job2 = Mock()

        pipeline1 = Pipeline(name, [job1])
        pipeline2 = Pipeline(name, [job2])

        self.assertNotEqual(pipeline2, pipeline1)

    def test_equal_by_name(self):
        """Checks that two pipelines are the same if they share the same name.
        """
        name = 'pipeline'

        pipeline1 = Pipeline(name)
        pipeline2 = Pipeline(name)

        self.assertEqual(pipeline2, pipeline1)

    def test_merge_pipeline(self):
        """Checks that the jobs from one pipeline is added to the other
        during a merge.
        """
        name1 = 'job1'
        name2 = 'job2'

        job1 = Mock()
        job1.name = Mock()
        job1.name.value = name1

        job2 = Mock()
        job2.name = Mock()
        job2.name.value = name2

        pipeline1 = Pipeline('pipeline1', {name1: job1})
        pipeline2 = Pipeline('pipeline2', {name2: job2})

        pipeline1.merge(pipeline2)

        self.assertEqual(
            {
                name1: job1,
                name2: job2
            },
            pipeline1.jobs.value
        )

    def test_merge_job(self):
        """Checks that a job that already exists on the pipeline gets merged
        instead of overwritten.
        """
        name = 'job'

        job = Mock()
        job.name = Mock()
        job.name.value = name
        job.merge = Mock()

        pipeline = Pipeline('pipeline', {name: job})

        pipeline.add_job(job)

        self.assertEqual(
            {
                name: job
            },
            pipeline.jobs.value
        )

        job.merge.assert_called_once_with(job)
