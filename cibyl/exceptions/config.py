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
from cibyl.exceptions import CibylException

from cibyl.utils.colors import Colors

class InvalidConfiguration(CibylException):
    """Invalid configuration exception"""

    def __init__(self, message=Colors.yellow("""
Invalid Configuration.
A valid configuration should specify an environment, its system(s) and the
system(s) details

environments:
    env_1:
        jenkins_system:
            system_type: jenkins""")):
        self.message = message
        super().__init__(self.message)


class ConfigurationNotFound(CibylException):
    """Configuration file not found exception"""
    def __init__(self, message="Could not find configuration file:"
                 "('~/.config/cibyl.yaml', '/etc/cibyl/cibyl.yaml')"):
        self.message = message
        super().__init__(self.message)
