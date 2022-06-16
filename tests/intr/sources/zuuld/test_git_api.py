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
import os
from copy import deepcopy
from unittest import TestCase

from cibyl.sources.zuuld.git_api import ZuulLocal

REPOS = {'repos': [{'url': 'https://localhost:8000/myrepo.git'}],
         'remote': False,
         'username': 'johnsnow',
         'token': "ghp_abcdefghijklmnopqrstvwaxyz_123456789"}


class TestZuulGitAPI(TestCase):
    def setUp(self) -> None:
        self.valid = deepcopy(REPOS)
        self.path = os.path.join(os.path.expanduser("~/.cibyl/"),
                                 "tripleo-ci")
        self.valid['repos'][0].update({
            "url": "https://github.com/openstack/tripleo-ci",
            "dest": self.path
        })

    def test_zuuld_kwargs(self):
        data = {'name': 'git',
                'driver': None,
                'enabled': True,
                'priority': 0,
                '_setup': False,
                '_down': False}
        self.assertEqual(data, ZuulLocal(REPOS))

    def test_zuuld_repos_with_valid_repo(self):
        data = ZuulLocal(self.valid)
        data._validate()
        self.assertEqual(os.path.isdir(self.path), True)

    def test_zuuld_repos_file_list(self):
        data = ZuulLocal(self.valid)
        data._validate()
        zuuld_files = data.get_file_list()
        expected_files = [os.path.join(self.path, "zuul.d", i)
                          for i in os.listdir(
                              os.path.join(self.path, "zuul.d"))
                          if i.endswith(".yaml") or i.endswith(".yml")]
        self.assertEqual(zuuld_files, expected_files)

    def test_zuuld_repos_with_parse_file(self):
        data = ZuulLocal(self.valid)
        yaml_file = os.path.join(self.path, "zuul.d",
                                 "ansible.yaml")
        yaml_data = data._parse_file(yaml_file)
        self.assertIn('project-template', yaml_data[0].keys())
