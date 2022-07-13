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

from tripleo.insights.tripleo import THTBranchCreator, THTPathCreator


class TestTHTBranchCreator(TestCase):
    """Tests for :class:`THTBranchCreator`.
    """

    def test_ignores_master(self):
        """Checks that the master branch is, by default, returned untouched.
        """
        release = 'master'

        creator = THTBranchCreator()

        self.assertEqual(
            f'{release}',
            creator.create_release_branch(release)
        )

    def test_creates_release_branch(self):
        """Checks the default template for a release branch.
        """
        release = 'wallaby'

        creator = THTBranchCreator()

        self.assertEqual(
            f'stable/{release}',
            creator.create_release_branch(release)
        )


class TestTHTPathCreator(TestCase):
    """Tests for :class:`THTPathCreator`.
    """

    def test_creates_scenario_path(self):
        """Checks the default template for a scenario path.
        """
        file = 'scenario001.yaml'

        creator = THTPathCreator()

        self.assertEqual(
            f'ci/environments/{file}',
            creator.create_scenario_path(file)
        )
