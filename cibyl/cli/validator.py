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
from typing import Callable, List, Tuple

from cibyl.exceptions.model import (InvalidEnvironment, InvalidSystem,
                                    NoEnabledSystem, NoValidSystem)
from cibyl.exceptions.source import NoValidSources
from cibyl.models.ci.base.environment import Environment
from cibyl.models.ci.base.system import System

LOG = logging.getLogger(__name__)


class Validator:
    """This is a helper class that will filter the configuration according to
    the user input.
    """

    def __init__(self, ci_args: dict):
        self.ci_args = ci_args

    def _check_input_environments(
            self, all_envs: List[str], argument: str,
            exception_to_raise: Callable[[str, List[str]], None]
    ) -> None:
        """Check if the user input environments exist in the configuration.

        :param all_envs: Environments defined in the configuration
        :param argument: Name of the cli argument to check
        :param exception_to_raise: Exception to be raised when input
                                   environment does not exist in the
                                   configuration
        :raises: :param: `exception_to_raise` (usually InvalidEnvironment
                          or InvalidSystem)
        """

        env_user_input = self.ci_args.get(argument)
        if env_user_input:
            # check if user input environment name exists
            for env_name in env_user_input.value:
                if env_name not in all_envs:
                    raise exception_to_raise(env_name, all_envs)

    def _consistent_environment(self, env: Environment) -> bool:
        """Check if an environment should be used according to user input.

        :param env: Model to validate
        :returns: Whether the environment is consistent with user input
        """
        user_env = self.ci_args.get("envs")
        if user_env:
            return env.name.value in user_env.value
        return True

    def _consistent_system(self, system: System) -> bool:
        """Check if a system should be used according to user input.

        :param system: Model to validate
        :returns: Whether the system is consistent with user input
        """
        name = system.name.value
        system_type = system.system_type.value

        user_system_type = self.ci_args.get("system_type")
        if user_system_type and system_type not in user_system_type.value:
            return False

        user_systems = self.ci_args.get("systems")
        if user_systems and name not in user_systems.value:
            return False

        return True

    def _system_has_valid_sources(self, system: System) -> bool:
        """Check if a system should be used according to user input from
        sources point of view.

        :param system: Model to validate
        :returns: Whether the system is consistent with user input
        """

        system_sources = set(source.name for source in system.sources)
        user_sources = self.ci_args.get("sources")
        if user_sources:
            user_sources_names = set(user_sources.value)
            unused_sources = system_sources - user_sources_names
            for source in system.sources:
                if source.name in unused_sources:
                    source.disable()
            if not user_sources_names & system_sources:
                return False

        return True

    def check_envs(self, environments: List[Environment],
                   systems_check: Callable[[System], bool],
                   envs_check: Callable[[Environment], bool],
                   systems_msg: str,
                   envs_msg: str) -> Tuple[List[Environment], List[System]]:
        """Iterate over environments and systems and apply some check to each
        of them. Only return those that satisfy the checks.

        :param environments: Environments to validate
        :param systems_check: Function to use to check a system
        :param envs_check: Function to use to check an environment
        :param systems_msg: Message template to log in case of system check
        failure
        :param envs_msg: Message template to log in case of environment check
        failure

        :returns: Environments and systems that pass the checks
        """
        user_systems = []
        user_envs = []
        for env in environments:
            env_systems = []
            if not envs_check(env):
                LOG.debug(envs_msg, env.name.value)
                continue
            for system in env.systems:
                if not systems_check(system):
                    LOG.debug(systems_msg, system.name.value)
                    continue
                env_systems.append(system)
            if env_systems:
                # if the environment has no valid systems, we will not pass it
                # back, so for the rest of the execution we will only consider
                # valid environments and systems
                env.systems.value = env_systems
                user_envs.append(env)
                user_systems.extend(env_systems)
        return user_envs, user_systems

    def _system_is_enabled(self, system: System) -> bool:
        """Check if a system should be used according to enabled parameter in
        configuration file.

        :param system: Model to validate
        :returns: Whether the system is enabled
        """
        return system.is_enabled()

    def override_enabled_systems(self, systems: List[System]) -> None:
        """Ensure that systems specified by the user with the --systems
        argument are enabled.

        :param systems: systems to check
        """

        user_systems = self.ci_args.get("systems")
        if not user_systems or not user_systems.value:
            # if the user did not specify anything for --systems, nothing to do
            # here
            return
        for system in systems:
            if system.name.value in user_systems.value:
                system.enable()

    def validate_environments(
            self, environments: List[Environment]
    ) -> List[Environment]:
        """Filter environments and systems according to user input.

        :returns: Environments and systems that can be used according to user
        input
        """
        all_envs = []
        all_systems = []
        # first get all environments and systems so we can ensure that the user
        # input is found within the configuration
        for env in environments:
            all_envs.append(env.name.value)
            for system in env.systems:
                all_systems.append(system)
        self._check_input_environments(all_envs, "envs",
                                       InvalidEnvironment)
        system_names = [system.name.value for system in all_systems]
        self._check_input_environments(system_names, "systems", InvalidSystem)

        # if the user input is good, then filter the environments and systems
        # so we only keep the ones consistent with user input
        user_envs, user_systems = self.check_envs(environments,
                                                  self._consistent_system,
                                                  self._consistent_environment,
                                                  "System %s is not consistent"
                                                  " with user input",
                                                  "Environment %s is not "
                                                  "consistent with user input")

        if not user_systems:
            raise NoValidSystem(system_names)

        self.override_enabled_systems(user_systems)

        user_envs, user_systems = self.check_envs(user_envs,
                                                  self._system_is_enabled,
                                                  lambda _: True,
                                                  "System %s is disabled ",
                                                  "")
        if not user_systems:
            raise NoEnabledSystem()

        system_sources_check = self._system_has_valid_sources
        user_envs, user_systems = self.check_envs(user_envs,
                                                  system_sources_check,
                                                  lambda _: True,
                                                  "System %s has no sources "
                                                  "consistent with user input",
                                                  "")
        if not user_systems:
            sources = [source['name'] for system in all_systems
                       for source in system.sources]
            raise NoValidSources(sources=sources)

        return user_envs
