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
import os
import re
import yaml

import xml.etree.ElementTree as ET

from functools import partial
from io import StringIO
from typing import Dict

from cibyl.cli.argument import Argument
from cibyl.exceptions.jenkins import JenkinsError
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.job import Job
from cibyl.plugins.openstack.container import Container
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.package import Package
from cibyl.plugins.openstack.service import Service
from cibyl.plugins.openstack.utils import translate_topology_string
from cibyl.sources.source import speed_index
from cibyl.utils.dicts import subset
from cibyl.sources.plugins import SourceExtension
from cibyl.utils.filtering import (DEPLOYMENT_PATTERN, DVR_PATTERN_NAME,
                                   IP_PATTERN, NETWORK_BACKEND_PATTERN,
                                   RELEASE_PATTERN, SERVICES_PATTERN,
                                   STORAGE_BACKEND_PATTERN, TOPOLOGY_PATTERN,
                                   apply_filters, filter_topology,
                                   satisfy_exact_match)

LOG = logging.getLogger(__name__)

TOPOLOGY = "[a-zA-Z0-9:,]+:[0-9]+" # e.g. controller:3,database:3,messaging:3,networker:2,compute:2
NODE_NAME_COUNTER = "[a-zA-Z]+:[0-9]+"

class JenkinsJobBuilder(SourceExtension):
    def _get_nodes(self, path, **kwargs):
        if "topology" in kwargs:
            topology = self._get_topology(path, **kwargs)
            nodes = {}
            for component in topology.split(","):
                role, amount = component.split(":")
                for i in range(int(amount)):
                    node_name = role + f"-{i}"
                    nodes[node_name] = Node(node_name, role=role)
            return nodes
        else:
            return {}

    def _get_topology(self, path, **kwargs):
        topology = ""
        if "topology" in kwargs:
            root = ET.parse(path).getroot()

            for script in root.iter("script"):
                file = StringIO(script.text)
                result = set([])
                with open(file) as f:
                    lines = [line.rstrip() for line in f if "TOPOLOGY=" in line or "TOPOLOGY =" in line]

                    for line in lines:
                        topology = re.findall(TOPOLOGY, line)
                        for t in topology:
                            nodes = re.findall(NODE_NAME_COUNTER, t)
                            nodeSet = set(nodes)
                            list = result.union(nodeSet)
                            topology = topology + ",".join(list)

            if topology == "" and kwargs['topology'].value is not None:
                return None
        return topology

    def _get_ip_version(self, path, **kwargs):
        if "ip_version" in kwargs:
            return "ipv4"
        else:
            return ""

    @speed_index({'base': 3})
    def get_deployment(self, **kwargs):
        jobs = {}
        for repo in self.repos:
            # filter according to jobs paramater if specified by kwargs
            jobs.update(self.get_jobs_from_repo(frozenset(repo.items()), **kwargs))

        for job_name in jobs:
            path = self._xml_files[job_name]

            topology = self._get_topology(path, **kwargs)

            # filter out jobs according to topology filter
            if topology is None and kwargs['topology'].value is not None:
                del jobs[job_name]
                continue

            deployment = Deployment(release = "",
                                    infra_type = "",
                                    nodes=self._get_nodes(path, **kwargs),
                                    services={},
                                    ip_version=self._get_ip_version(path, **kwargs),
                                    ml2_driver="",
                                    topology= topology,
                                    network_backend="",
                                    storage_backend="",
                                    dvr="",
                                    ironic_inspector="",
                                    cleaning_network="",
                                    tls_everywhere="",
                                    security_group="")

            jobs[job_name].add_deployment(deployment)

        return AttributeDictValue("jobs", attr_type=Job, value=jobs)