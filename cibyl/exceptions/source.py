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


class TooManyValidSources(Exception):
    """Exception for trying to use multiple supported sources."""

    def __init__(self, system):
        self.system = system
        self.message = f"""You have more than one source defined for the system
 {self.system}.
Please either specify one source with --source argument or set higher
priority for the source
in the configuration, this way:

environments:
    env_1:
        jenkins_system:
            system_type: jenkins
                 sources:
                   jenkins:
                     priority: 1
"""
        super().__init__(self.message)


class NoSupportedSourcesFound(Exception):
    """Exception for a case where non of the sources of a single system is
       implementing the function of the argument the user is interested in
    """

    def __init__(self, system, function):
        self.message = f"""Couldn't find any source for the system {system}
that implements the function {function}
"""
        super().__init__(self.message)


class NoValidSources(Exception):
    """Exception for a case when no valid source is found."""

    def __init__(self, system):
        self.system = system
        self.message = f"""No valid source defined for the system
{self.system}.  Please ensure the specified sources with --source argument
are present in the configuration.
"""
        super().__init__(self.message)
