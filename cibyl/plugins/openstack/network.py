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
from typing import Optional

from cibyl.cli.argument import Argument
from cibyl.models.model import Model

# pylint: disable=no-member


class Network(Model):
    """Network properties of an openstack deployment"""

    API = {
        'ip_version': {
            'attr_type': str,
            'arguments': [Argument(name='--ip-version', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Ip version used in the "
                                               "deployment")]
        },
        'ml2_driver': {
            'attr_type': str,
            'arguments': [Argument(name='--ml2-driver', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="ML2 driver used in the "
                                               "deployment")]
        },
        'dvr': {
            'arguments': []
        },
        'tls_everywhere': {
            'arguments': []
        },
        'security_group': {
            'arguments': []
        },
        'network_backend': {
            'attr_type': str,
            'arguments': [Argument(name='--network-backend', arg_type=str,
                                   func='get_deployment', nargs='*',
                                   description="Network backend used in the "
                                               "deployment")]
        },
    }

    def __init__(self, ip_version: Optional[str] = None,
                 network_backend: Optional[str] = None,
                 dvr: Optional[str] = None,
                 tls_everywhere: Optional[str] = None,
                 ml2_driver: Optional[str] = None,
                 security_group: Optional[str] = None):
        super().__init__({
                          'ip_version': ip_version,
                          'network_backend': network_backend,
                          'dvr': dvr, 'tls_everywhere': tls_everywhere,
                          'ml2_driver': ml2_driver,
                          'security_group': security_group})

    def merge(self, other: 'Network') -> None:
        """Merge the information of two deployment objects representing the
        same deployment.

        :param other: The Deployment object to merge
        """
        if not self.ip_version.value:
            self.ip_version.value = other.ip_version.value
        if not self.network_backend.value:
            self.network_backend.value = other.network_backend.value
        if not self.dvr.value:
            self.dvr.value = other.dvr.value
        if not self.tls_everywhere.value:
            self.tls_everywhere.value = other.tls_everywhere.value
        if not self.ml2_driver.value:
            self.ml2_driver.value = other.ml2_driver.value
        if not self.security_group.value:
            self.security_group.value = other.security_group.value
