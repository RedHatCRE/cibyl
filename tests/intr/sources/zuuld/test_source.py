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
from copy import deepcopy
from unittest import TestCase
from unittest.mock import Mock

from cibyl.models.attribute import AttributeDictValue
from cibyl.sources.zuuld.git_api import ZuulGitHub, ZuulLocal
from cibyl.sources.zuuld.source import ZuulD

REPOS = {'repos': [{'url': 'https://github.com/openstack/tripleo-ci.git'}],
         'remote': False,
         'username': 'johnsnow',
         'token': "ghp_abcdefghijklmnopqrstvwaxyz_123456789"}


class TestZuulDSource(TestCase):
    def setUp(self) -> None:
        self.name = 'zuul_source'
        self.driver = 'zuul.d'

    def test_zuuld_source(self):
        zuul = ZuulD(self.name, self.driver, **REPOS)
        self.assertEqual(zuul.name, self.name)
        self.assertEqual(zuul.driver, self.driver)
        self.assertEqual(zuul.repos, REPOS['repos'])

    def test_zuuld_source_github(self):
        repos = deepcopy(REPOS)
        repos['remote'] = True
        zuul = ZuulD(self.name, self.driver, **repos)
        self.assertTrue(isinstance(zuul.api, ZuulGitHub))

    def test_zuuld_source_zuullocal(self):
        zuul = ZuulD(self.name, self.driver, **REPOS)
        self.assertTrue(isinstance(zuul.api, ZuulLocal))

    def test_zuud_source_get_jobs(self):
        zuul = Mock(name=self.name, driver=self.driver, kwargs=REPOS)
        zuul.get_jobs = Mock()

        data = ZuulD(self.name, self.driver, **REPOS).get_jobs()
        self.assertTrue(isinstance(data, AttributeDictValue))
