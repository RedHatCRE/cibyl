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

from cibyl.sources.zuuld.backends.git import YAMLHandle
from cibyl.sources.zuuld.models.job import Job
from kernel.tools.fs import File


class TestYAMLHandle(TestCase):
    """Tests for :class:`YAMLHandle`.
    """

    def test_reads_jobs(self):
        """Checks that the handler is able to form the jobs from a valid
        collection of data.
        """
        job1 = {
            'name': 'job1'
        }

        job2 = {
            'name': 'job2',
            'parent': 'job1',
            'branches': 'devel'
        }

        job3 = {
            'name': 'job3',
            'parent': 'job2',
            'branches': ['master'],
            'vars': {
                'my_var': 'my_val'
            }
        }

        data = [job1, job2, job3]

        handle = YAMLHandle(
            data=data,
            schema=File('cibyl/_data/schemas/zuuld.json')
        )

        result = list(handle.read_jobs())

        self.assertEqual(
            Job(
                name=job1['name']
            ),
            result[0]
        )

        self.assertEqual(
            Job(
                name=job2['name'],
                parent=job1['name'],
                branches=[job2['branches']]
            ),
            result[1]
        )

        self.assertEqual(
            Job(
                name=job3['name'],
                parent=job2['name'],
                branches=job3['branches'],
                vars=job3['vars']
            ),
            result[2]
        )
