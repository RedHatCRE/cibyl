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
from cibyl.plugins.openstack.sources import jenkins_job_builder
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
# grep network-protocol * -rn  | awk '{ $1=""; print $0; }' | sort -u
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

# add everything relevant manually from the results of
# grep send_results_to_umb * -rn  | awk '{ $1=""; print $0; }' | sort -u
release_content = [
    # ------------------------  release
    {
        "str": "<pattern>rhos-10.0-patches</pattern>",
        "kwargs": {
            'release': Argument("release", str, "", value=[])},
        "res": "10.0"},
    {
        "str": "<pattern>rhos-16.1-trunk-patches|rhos-16.1-patches|rhos-16.1-trunk-patches</pattern>",  # noqa: E501
        "kwargs": {
            'release': Argument("release", str, "", value=[])},
        "res": "16.1"},
    {
        "str": "RefSpecName = &quot;+refs/heads/rhos-10.0-patches:refs/remotes/origin/rhos-10.0-patches&quot;",  # noqa: E501
        "kwargs": {
            'release': Argument("release", str, "", value=[])},
        "res": "10.0"},
    {
        "str": "RefSpecName = &quot;+refs/heads/rhos-10.0-patches:refs/remotes/origin/rhos-10.0-patches&quot;",  # noqa: E501
        "kwargs": {
            'release': Argument("release", str, "", value=[10.0])},
        "res": "10.0"},
    {
        "str": "RefSpecName = &quot;+refs/heads/rhos-10.0-patches:refs/remotes/origin/rhos-10.0-patches&quot;",  # noqa: E501
        "kwargs": {
            'release': Argument("release", str, "", value=[17.0])},
        "res": None},
]

# add everything relevant manually from the results of
# grep IR_TRIPLEO_OVERCLOUD_STORAGE_BACKEND_UPD * -rn  | awk '{ $1=""; print $0; }' | sort -u  # noqa: E501
# grep storage-backend * -rn  | awk '{ $1=""; print $0; }' | sort -u
cinder_backup_content = [
    # ------------------------  cinder_backup
    {
        "str": " IR_TRIPLEO_OVERCLOUD_STORAGE_BACKEND_UPD = 'lvm'",
        "kwargs": {
            'cinder_backend': Argument("cinder_backend", str, "", value=[])},
        "res": "lvm"},
    {
        "str": "--storage-backend swift",
        "kwargs": {
            'cinder_backend': Argument("cinder_backend", str, "", value=[])},
        "res": "swift"},
    {
        "str": "--storage-backend swift",
        "kwargs": {
            'cinder_backend': Argument("cinder_backend", str, "", value=["lvm"])},  # noqa: E501
        "res": None},
]
infra_type_content = [
    {
        "str": " <defaultValue>--deployment-files composable_roles",
        "kwargs": {"infra_type": Argument("intra_type", str, "", value=[])},
        "res": "virt"},
    {
        "str": " --deployment-files bm_templates_link \\ ",
        "kwargs": {"infra_type": Argument("intra_type", str, "", value=[])},
        "res": "baremetal"},
    {
        "str": " --deployment-files ovb \\ ",
        "kwargs": {"infra_type": Argument("intra_type", str, "", value=[])},
        "res": "ovb"},
    {
        "str": " --deployment-files virt",
        "kwargs": {"infra_type": Argument("intra_type", str, "", value=[])},
        "res": "virt"},
    {
        "str": " --deployment-files virt \\ ",
        "kwargs": {"infra_type": Argument("intra_type", str, "", value=[])},
        "res": "virt"},
    {
        "str": " --deployment-files virt",
        "kwargs": {"infra_type": Argument("intra_type", str, "",
                                          value=["virt"])},
        "res": "virt"},
    {
        "str": " --deployment-files virt \\ ",
        "kwargs": {"infra_type": Argument("intra_type", str, "",
                                          value=["ovb"])},
        "res": None}
]


class TestJJBSourceOpenstackPlugin(OpenstackPluginWithJobSystem):
    def setUp(self):
        job_name = "job1"
        self.jjb = JenkinsJobBuilder()
        self.jjb.get_jobs_from_repo = Mock(
            side_effect=[{job_name: Job(name=job_name)}])
        self.jjb.repos = [{'url': 'url', 'dest': 'dest', 'cloned': True}]
        self.jjb._xml_files = MagicMock()

        logging.disable(logging.CRITICAL)

    def test_get_topology(self):
        for el in tolology_content:
            jenkins_job_builder.parse_xml = Mock(
                side_effect=[StringIO(el['str'])])
            self.assertEqual(
                self.jjb._get_topology("path.xml", **el['kwargs']),
                el['res'])

    def test_get_ipv(self):
        for el in ipv_content:
            jenkins_job_builder.parse_xml = Mock(
                side_effect=[StringIO(el['str'])])
            self.assertEqual(
                self.jjb._get_ip_version("path.xml", **el['kwargs']),
                el['res'])

    def test_get_release(self):
        for el in release_content:
            jenkins_job_builder.parse_xml = Mock(
                side_effect=[StringIO(el['str'])])
            self.assertEqual(
                self.jjb._get_release("path.xml", **el['kwargs']),
                el['res'])

    def test_get_cinder_backend(self):
        for el in cinder_backup_content:
            jenkins_job_builder.parse_xml = Mock(
                side_effect=[StringIO(el['str'])])
            self.assertEqual(
                self.jjb._get_cinder_backend("path.xml", **el['kwargs']),
                el['res'])

    def test_get_infra_type(self):
        for el in infra_type_content:
            jenkins_job_builder.parse_xml = Mock(
                side_effect=[StringIO(el['str'])])
            self.assertEqual(
                self.jjb._get_infra_type("path.xml", **el['kwargs']),
                el['res'])
