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

from cibyl.sources.zuuld.frontends.zuul import GitFrontendFactory


class TestGitFrontendFactory(TestCase):
    """Tests for :class:`GitFrontendFactory`.
    """

    def test_error_in_from_kwargs_for_no_repos(self):
        """Checks that if kwargs are missing the 'repos' key, an error is
        raised.
        """
        with self.assertRaises(ValueError):
            GitFrontendFactory.from_kwargs()
