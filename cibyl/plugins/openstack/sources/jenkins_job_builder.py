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
import logging
import re
import xml.etree.ElementTree as ET
from io import StringIO

from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.job import Job
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.plugins.openstack.node import Node
from cibyl.sources.plugins import SourceExtension
from cibyl.sources.source import speed_index

LOG = logging.getLogger(__name__)

# e.g. controller:3,database:3,messaging:3,networker:2,compute:2
TOPOLOGY = "[a-zA-Z0-9:,]+:[0-9]+"
NODE_NAME_COUNTER = "[a-zA-Z]+:[0-9]+"


class JenkinsJobBuilder(SourceExtension):
    def _get_nodes(self, path, **kwargs):
        topology = self._get_topology(path, **kwargs)
        nodes = {}
        for component in topology.split(","):
            role, amount = component.split(":")
            for i in range(int(amount)):
                node_name = role + f"-{i}"
                nodes[node_name] = Node(node_name, role=role)
        return nodes

    def _get_topology(self, path, **kwargs):
        topology_str = ""
        if "topology" in kwargs:
            root = ET.parse(path).getroot()
            result = set([])
            for script in root.iter("script"):
                file = StringIO(script.text)
                lines = [line.rstrip() for line in file if
                         "TOPOLOGY=" in line or "TOPOLOGY =" in line]
                for line in lines:
                    topology_lst = re.findall(TOPOLOGY, line)
                    for el in topology_lst:
                        nodeSet = set(re.findall(NODE_NAME_COUNTER, el))
                        result = result.union(nodeSet)
            topology_str = ",".join(result)
            # e.g. --topology cont, --topology controller:3
            if kwargs['topology'].value is not None and len(
                    list(filter(lambda x: kwargs['topology'].value[0] in x,
                                result))) == 0:
                return None

        return topology_str

    def _get_ip_version(self, path, **kwargs):
        if "ip_version" in kwargs:
            return "ipv4"
        else:
            return ""

    @speed_index({'base': 3})
    def get_deployment(self, **kwargs):

        filterted_out = []
        jobs = {}
        for repo in self.repos:
            # filter according to jobs parameter if specified by kwargs
            jobs.update(
                self.get_jobs_from_repo(frozenset(repo.items()), **kwargs))

        for job_name in jobs:
            path = self._xml_files[job_name]

            topology = self._get_topology(path, **kwargs)

            # compute what is filtered out according to topology filter
            if topology is None and kwargs['topology'].value is not None:
                filterted_out += [job_name]
                continue

            deployment = Deployment("",
                                    "",
                                    nodes=self._get_nodes(path, **kwargs),
                                    services={},
                                    topology=topology,
                                    network="",
                                    storage="",
                                    ironic="",
                                    test_collection="",
                                    overcloud_templates="",
                                    stages="")

            jobs[job_name].add_deployment(deployment)

        # filter out jobs
        for el in filterted_out:
            del jobs[el]

        return AttributeDictValue("jobs", attr_type=Job, value=jobs)
