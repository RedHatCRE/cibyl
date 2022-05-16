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
from enum import Enum

from cibyl.models.ci.base.system import JobsSystem
from cibyl.models.ci.zuul.system import ZuulSystem


class SystemType(str, Enum):
    """Describes the systems known by the app, those which can be build.
    """
    JENKINS = 'jenkins'
    ZUUL = 'zuul'


class SystemFactory:
    """Instantiates systems from inputs coming from the configuration file.
    """

    @staticmethod
    def create_system(system_type, name, **kwargs):
        """Builds a new system.

        :param system_type: Type of the system to build.
        :type system_type: str or :class:`SourceType`
        :param name: A name to identify the system.
        :type name: str
        :param kwargs: Collection of data that further describes the system.
        :return: A new instance.
        :rtype: :class:`cibyl.systems.system.Source`
        """
        system_type = system_type.lower()

        if system_type == SystemType.JENKINS:
            return JobsSystem(name=name, system_type=system_type, **kwargs)

        if system_type == SystemType.ZUUL:
            return ZuulSystem(name=name, system_type=system_type, **kwargs)

        msg = f"Unknown system type '{system_type}'"
        raise NotImplementedError(msg)
