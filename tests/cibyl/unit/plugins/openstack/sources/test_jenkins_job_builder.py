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
# pylint: disable=no-member
import logging
from io import StringIO
from unittest.mock import MagicMock, Mock

from cibyl.cli.argument import Argument
from cibyl.models.ci.base.job import Job
from cibyl.plugins.openstack.sources.jenkins_job_builder import \
    JenkinsJobBuilder
from tests.cibyl.utils import OpenstackPluginWithJobSystem

# add everything relevant manually from the results of
# grep "TOPOLOGY =|TOPOLOGY=" * -rn  | awk '{ $1=""; print $0; }' | sort -u
tolology_content = [
    {
        "str": "TOPOLOGY = env.TOPOLOGY?.trim() ?: &quot;controller:1,compute:1,ceph:1,freeipa:1&quot;",  # noqa: E501
        "kwargs": {
            'topology': Argument("topology", str, "", value=[])},
        "res": "ceph:1,compute:1,controller:1,freeipa:1"},
    {
        "str": "TOPOLOGY = \"bmc:1,${TOPOLOGY}\"",
        "kwargs": {
            'topology': Argument("topology", str, "", value=[])},
        "res": "bmc:1"},
    {
        "str": "TOPOLOGY -= 'undercloud:1,'",
        "kwargs": {
            'topology': Argument("topology", str, "", value=[])},
        "res": ""},
]

# add everything relevant manually from the results of
# grep network-protocol * -rn  | awk '{ print $2 " " $3;}' | sort -u
ipv_content = [
    # ------------------------  ip-version
    {
        "str": "--network-protocol ipv4&quot;",
        "kwargs": {
            'ip_version': Argument("ip_version", str, "", value=[4])},
        "res": "4"},
    {
        "str": "--network-protocol ipv4&quot;",
        "kwargs": {
            'ip_version': Argument("ip_version", str, "", value=[6, 4])},
        "res": "4"},
    {
        "str": "--network-protocol ipv6&quot;",
        "kwargs": {
            'ip_version': Argument("ip_version", str, "", value=[])},
        "res": "6"},
    {
        "str": "ipv4&quot;",
        "kwargs": {
            'ip_version': Argument("ip_version", str, "", value=[])},
        "res": ""},
    {
        "str": "ipv6-all&quot;",
        "kwargs": {
            'ip_version': Argument("ip_version", str, "", value=[])},
        "res": ""},
    {
        "str": "ipv6&quot;",
        "kwargs": {
            'ip_version': Argument("ip_version", str, "", value=[])},
        "res": ""},
    {
        "str": "--network-protocol ipv6-all&quot;",
        "kwargs": {
            'ip_version': Argument("ip_version", str, "", value=[])},
        "res": "6"},

]


class TestJJBSourceOpenstackPlugin(OpenstackPluginWithJobSystem):
    def setUp(self):
        job_name = "job1"
        self.path = "path1"
        self.jjb = JenkinsJobBuilder()
        self.jjb.get_jobs_from_repo = Mock(
            side_effect=[{job_name: Job(name=job_name)}])
        self.jjb.repos = [{'url': 'url', 'dest': 'dest', 'cloned': True}]
        self.jjb._xml_files = MagicMock()[self.path]

        logging.disable(logging.CRITICAL)

    def test_get_topology(self):
        for el in tolology_content:
            self.jjb._parse_xml = Mock(side_effect=[StringIO(el['str'])])
            self.assertEqual(self.jjb._get_topology(self.path, **el['kwargs']),
                             el['res'])

    def test_get_ipv(self):
        for el in ipv_content:
            self.jjb._parse_xml = Mock(side_effect=[StringIO(el['str'])])
            self.assertEqual(
                self.jjb._get_ip_version(self.path, **el['kwargs']),
                el['res'])
