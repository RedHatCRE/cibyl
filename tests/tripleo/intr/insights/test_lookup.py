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

from kernel.tools.cache import CACache
from kernel.tools.urls import URL
from tripleo.insights import DeploymentOutline
from tripleo.insights.interpreters import (FeatureSetInterpreter,
                                           ReleaseInterpreter)
from tripleo.insights.lookup import Resource, ScenarioFactory


class TestScenarioFactory(TestCase):
    """Tests for :class:`ScenarioFactory`.
    """

    def test_merges_environments(self):
        """Checks that the resulting interpreter works with the combined
        data from all interpreter files found on the featureset.
        """
        rkeys = ReleaseInterpreter.Keys()
        fskeys = FeatureSetInterpreter.Keys()

        url = URL('http://localhost:8080')
        branch = 'master'

        res1 = Resource(
            repo=url,
            file='path/to/file/A.yaml',
            branch=branch
        )

        res2 = Resource(
            repo=url,
            file='path/to/file/B.yaml',
            branch=branch
        )

        cache = CACache()

        cache.put(
            res1,
            {
                'A': {
                    'a': 1
                },
                'B': 1
            }
        )

        cache.put(
            res2,
            {
                'A': {
                    'a': 2
                },
                'C': [
                    2
                ]
            }
        )

        outline = DeploymentOutline(
            heat=url
        )

        featureset = FeatureSetInterpreter(
            data={
                fskeys.environments: [res1.file, res2.file]
            }
        )

        release = ReleaseInterpreter(
            data={
                rkeys.release: branch
            }
        )

        factory = ScenarioFactory(cache)

        result = factory.from_interpreters(outline, featureset, release)

        self.assertEqual(
            {
                'A': {
                    'a': 2
                },
                'B': 1,
                'C': [
                    2
                ]
            },
            result.data
        )
