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

LOG = logging.getLogger(__name__)
SHORT_TOPOLOGY_PATTERN = re.compile(r"(\d)+(.*)")


class TopologyAbbreviations:
    """Translate the typical abbreviation used in the topology of openstack
    deployments."""
    abbreviations = {'comp': 'compute', 'cont': 'controller', 'ceph': 'ceph',
                     'freeipa': 'freeipa', 'net': 'networker',
                     'novactl': 'novacontrol'}

    @staticmethod
    def translate(abbreviation):
        """Translate an abbreviation into a long form name of a component of an
        openstack deployment topology. If the short form does not have a long
        form associated, return the short form.

        :param abbreviation: Short form of the component
        :type abbreviation: str
        :returns: The long form name of the component
        :rtype: str
        """
        return TopologyAbbreviations.abbreviations.get(abbreviation,
                                                       abbreviation)


def translate_topology_string(short_topology: str):
    """Translate a topology string in short form (as typically found in job
    names) to a long form one.

    :param short_topology: Openstack topology in short form
    :type short_topology: str
    :returns: The long form topology string
    :rtype: str
    """
    topology = short_topology.split("_")
    long_topology = []
    for component in topology:
        match_string = SHORT_TOPOLOGY_PATTERN.search(component)
        if not match_string:
            LOG.debug("component %s in topology string %s not identified",
                      component, short_topology)
            continue
        number = match_string.group(1)
        component_long = TopologyAbbreviations.translate(match_string.group(2))
        long_topology.append(f"{component_long}:{number}")
    return ",".join(long_topology)
