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

from cibyl.exceptions.model import NoValidEnvironment, NoValidSystem

LOG = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class Validator:
    """This is a helper class that will filter the configuration according to
    the user input.
    """

    def __init__(self, ci_args: dict):
        self.ci_args = ci_args

    def _consistent_environment(self, env):
        """Check if an environment should be used according to user input.

        :param env: Model to validate
        :type env: :class:`.Environment`
        :returns: Whether the environment is consistent with user input
        :rtype: bool
        """
        user_env = self.ci_args.get("env_name")
        if user_env:
            return env.name.value in user_env.value
        return True

    def _consistent_system(self, system):
        """Check if a system should be used according to user input.

        :param system: Model to validate
        :type system: :class:`.System`
        :returns: Whether the system is consistent with user input
        :rtype: bool
        """
        is_valid_system = True
        name = system.name.value
        system_type = system.system_type.value

        user_system_type = self.ci_args.get("system_type")
        if user_system_type and system_type not in user_system_type.value:
            is_valid_system = False

        user_system_name = self.ci_args.get("system_name")
        if user_system_name and name not in user_system_name.value:
            is_valid_system = False

        user_systems = self.ci_args.get("systems")
        if user_systems and name not in user_systems.value:
            is_valid_system = False

        return is_valid_system

    def validate_environments(self, environments):
        """Filter environments and systems according to user input.

        :returns: Systems that can be used according to user input
        :rtype: dict
        """
        user_systems = []
        user_envs = []
        for env in environments:
            if not self._consistent_environment(env):
                LOG.debug("Environment %s is not consistent with user input",
                          env.name.value)
                continue
            user_envs.append(env)
            for system in env.systems:
                if not self._consistent_system(system):
                    LOG.debug("System %s is not consistent with user input",
                              system.name.value)
                    continue
                user_systems.append(system)

        if not user_envs:
            raise NoValidEnvironment()
        if not user_systems:
            raise NoValidSystem()
        return user_envs, user_systems
