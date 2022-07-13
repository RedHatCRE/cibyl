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

from cibyl.plugins.openstack.sources.zuul.tripleo import (
    QuickStartFileCreator, QuickStartPathCreator)


class TestQuickStartFileCreator(TestCase):
    """Tests for :class:`QuickStartFileCreator`.
    """

    def test_default_featureset_template(self):
        """Checks that the default featureset template produces the desired
        file names.
        """
        number = '052'

        creator = QuickStartFileCreator()

        self.assertEqual(
            f'featureset{number}.yml',
            creator.create_featureset(number)
        )

    def test_default_nodes_template(self):
        """Checks that the default nodes template produces the desired file
        names.
        """
        node = 'node'

        creator = QuickStartFileCreator()

        self.assertEqual(
            f'{node}.yml',
            creator.create_nodes(node)
        )

    def test_default_release_template(self):
        """Checks that the default release template produces the desired
        file names.
        """
        release = 'release'

        creator = QuickStartFileCreator()

        self.assertEqual(
            f'{release}.yml',
            creator.create_release(release)
        )


class TestQuickStartPathCreator(TestCase):
    """Tests for :class:`QuickStartPathCreator`.
    """

    def test_environment_path(self):
        """Checks that paths to an environment are correct.
        """
        file = 'default_libvirt.yml'

        creator = QuickStartPathCreator()

        self.assertEqual(
            f'config/environments/{file}',
            creator.create_environment_path(file)
        )

    def test_featureset_path(self):
        """Checks that paths to a featureset are correct.
        """
        file = 'featureset052.yml'

        creator = QuickStartPathCreator()

        self.assertEqual(
            f'config/general_config/{file}',
            creator.create_featureset_path(file)
        )

    def test_nodes_path(self):
        """Checks that paths to nodes are correct.
        """
        file = '1ctlr.yml'

        creator = QuickStartPathCreator()

        self.assertEqual(
            f'config/nodes/{file}',
            creator.create_nodes_path(file)
        )

    def test_release_path(self):
        """Checks that paths to a release are correct.
        """
        file = 'wallaby.yml'

        creator = QuickStartPathCreator()

        self.assertEqual(
            f'config/release/{file}',
            creator.create_release_path(file)
        )
