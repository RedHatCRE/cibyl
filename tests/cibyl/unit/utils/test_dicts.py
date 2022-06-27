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

from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.build import Build
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.zuul.project import Project
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.utils.dicts import (chunk_dictionary_into_lists, intersect_models,
                               nsubset, subset)


class TestSubset(TestCase):
    """Test subset function of utils.dicts module."""
    def test_subset_is_generated(self):
        """Checks that this is capable of creating a dictionary from another.
        """
        original = {
            'a': 1,
            'b': 2,
            'c': 3
        }

        keys = ['a', 'c']

        self.assertEqual(
            {
                'a': 1,
                'c': 3
            },
            subset(original, keys)
        )


class TestNSubset(TestCase):
    def test_subset_is_generated(self):
        """Checks that this is capable of creating a dictionary from another.
        """
        original = {
            'a': 1,
            'b': 2,
            'c': 3
        }

        keys = ['a', 'c']

        self.assertEqual(
            {
                'b': 2
            },
            nsubset(original, keys)
        )


class TestChunkDictionaryResult(TestCase):
    def test_chunk_dictionary_result(self):
        """Checks that this is able to create a list with sub lists
        as chunk mode using the keys of a dictionary and the quantity
        of each one of the sub lists
        """
        # Create a dictionary of 500 keys:
        dictionary = {k: k for k in range(500)}
        sublist_size = 200
        lists = chunk_dictionary_into_lists(
            dictionary,
            sublist_size
        )
        # 500 / 200 = 2.5 so we should have:
        # 2 sub lists of 200
        # 1 sub list of the rest: 100
        self.assertEqual(3, len(lists))
        self.assertEqual(200, len(lists[0]))
        self.assertEqual(200, len(lists[1]))
        self.assertEqual(100, len(lists[2]))


class TestIntersectModels(TestCase):
    """Test intersect_models function of utils.dicts module."""
    def test_intersect_jobs(self):
        """Test that intersect_models filters correctly the models."""
        jobs1 = {"job1": Job("job1", url="url"), "jobs2": Job("job2")}
        jobs2 = {"job1": Job("job1"), "jobs3": Job("job3")}
        models1 = AttributeDictValue("models1", attr_type=Job,
                                     value=jobs1)
        models2 = AttributeDictValue("models2", attr_type=Job,
                                     value=jobs2)
        intersection = intersect_models(models1, models2)
        self.assertEqual(len(intersection), 1)
        job = intersection["job1"]
        self.assertEqual(job.name.value, "job1")
        self.assertEqual(job.url.value, "url")

    def test_intersect_jobs_with_builds(self):
        """Test that intersect_models filters correctly the models and
        incorporates information that is present in only one of them."""
        builds = {"1": Build("1", status="SUCCESS")}
        jobs1 = {"job1": Job("job1"), "jobs2": Job("job2")}
        jobs2 = {"job1": Job("job1", url="url", builds=builds),
                 "jobs3": Job("job3")}
        models1 = AttributeDictValue("models1", attr_type=Job,
                                     value=jobs1)
        models2 = AttributeDictValue("models2", attr_type=Job,
                                     value=jobs2)
        intersection = intersect_models(models1, models2)
        self.assertEqual(len(intersection), 1)
        job = intersection["job1"]
        self.assertEqual(job.name.value, "job1")
        self.assertEqual(job.url.value, "url")
        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 1)
        build = builds_found["1"]
        self.assertEqual(build.build_id.value, "1")
        self.assertEqual(build.status.value, "SUCCESS")

    def test_intersect_tenants_with_builds(self):
        """Test that intersect_models filters correctly the models and
        incorporates information that is present in only one of them."""
        builds = {"1": Build("1", status="SUCCESS")}
        jobs = {"job1": Job("job1", builds=builds), "jobs2": Job("job2")}
        projects1 = {"project1": Project("project1", "url")}
        projects2 = {"project2": Project("project2", "url")}
        tenant1 = {"tenant1": Tenant("tenant1", projects=projects1),
                   "tenants2": Tenant("tenant2")}
        tenant2 = {"tenant1": Tenant("tenant1", jobs=jobs, projects=projects2),
                   "tenants3": Tenant("tenant3")}
        models1 = AttributeDictValue("models1", attr_type=Tenant,
                                     value=tenant1)
        models2 = AttributeDictValue("models2", attr_type=Tenant,
                                     value=tenant2)
        intersection = intersect_models(models1, models2)
        self.assertEqual(len(intersection), 1)
        tenant = intersection["tenant1"]
        self.assertEqual(tenant.name.value, "tenant1")
        projects_found = tenant.projects.value
        self.assertEqual(len(projects_found), 2)
        self.assertEqual(len(projects_found), 2)
        self.assertIn("project1", projects_found)
        self.assertIn("project2", projects_found)
        jobs_found = tenant.jobs.value
        self.assertEqual(len(jobs_found), 2)
        self.assertEqual(len(jobs_found), 2)
        self.assertIn("job1", jobs_found)
        self.assertIn("job2", jobs_found)
        job = jobs_found["job1"]
        self.assertEqual(job.name.value, "job1")
        builds_found = job.builds.value
        self.assertEqual(len(builds_found), 1)
        build = builds_found["1"]
        self.assertEqual(build.build_id.value, "1")
        self.assertEqual(build.status.value, "SUCCESS")
