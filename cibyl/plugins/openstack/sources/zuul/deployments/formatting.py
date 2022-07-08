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
from string import Template

from tripleo.insights.io import Topology


class TopologyPrinter:
    """Utility used to produce a textual description of a topology model.
    """
    DEFAULT_TEMPLATE: Template = Template(
        'compute:$compute,'
        'controller:$ctrl,'
        'ceph:$ceph,'
        'cell:$cell'
    )
    """Default output format."""

    def __init__(self, template: Template = DEFAULT_TEMPLATE):
        """Constructor.

        :param template: Template this will use to generate the text out of
            the model. This template takes as many parameters as the model
            has items, all of them following the same name.
        """
        self._template = template

    @property
    def template(self):
        """
        :return: Template this will use to generate the text out of
            the model.
        """
        return self._template

    def print(self, topology: Topology) -> str:
        """Generate a textual representation of the topology model.

        :param topology: The model to translate.
        :return: A description of the model.
        """
        return self._template.substitute(
            compute=topology.compute,
            ctrl=topology.ctrl,
            ceph=topology.ceph,
            cell=topology.cell
        )
