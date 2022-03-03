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

LOG = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class Publisher:
    """Represents a publisher which is responsible for publishing the data
    collected by the application in the chosen format and to the chosen
    location
    """

    @staticmethod
    def publish(environments, dest="terminal"):
        """Publishes the data of the given environments to the
        chosen destination.
        """
        if dest == "terminal":
            for env in environments:
                print(env)
