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
from dataclasses import dataclass, field
from typing import Optional

from tripleo.insights.defaults import (DEFAULT_ENVIRONMENT_FILE,
                                       DEFAULT_FEATURESET_FILE,
                                       DEFAULT_NODES_FILE, DEFAULT_QUICKSTART,
                                       DEFAULT_RELEASE_FILE, DEFAULT_THT)
from tripleo.insights.topology import Topology
from tripleo.utils.urls import URL


@dataclass
class DeploymentOutline:
    """Defines the input data required to form the deployment summary.
    """
    quickstart: URL = DEFAULT_QUICKSTART
    """URL of TripleO QuickStart repository."""
    heat: URL = DEFAULT_THT
    """URL of Triple Heat Templates repository."""

    environment: str = DEFAULT_ENVIRONMENT_FILE
    """Path to environment file relative to the repository's root."""
    featureset: str = DEFAULT_FEATURESET_FILE
    """Path to featureset file relative to the repository's root."""
    nodes: str = DEFAULT_NODES_FILE
    """Path to nodes file relative to the repository's root."""
    release: str = DEFAULT_RELEASE_FILE
    """Path to release file relative to the repository's root."""

    overrides: dict = field(default_factory=lambda: {})
    """Defines the collection of deployment items that will override those
    coming from the deployment's files. The dictionary is meant to have the
    format: YAML item -> New value. On any case, the items on the dictionary
    must follow the same item naming and value types as the original file.

    This can be used as a way of altering the deployment without the need of
    modifying the files. For example, this dictionary: {'overcloud_ipv6' :
    True } will force the featureset to use IPv6.
    """


@dataclass
class DeploymentSummary:
    """Defines the deployment that TripleO will perform based on the
    outline provided as input.

    Every field left as 'None' indicates that no information related to it
    could be found. Interpret it as missing content.
    """

    @dataclass
    class Components:
        """Holds information on each of the deployed components.
        """

        @dataclass
        class Cinder:
            """Information on the Cinder component.
            """
            backend: Optional[str] = None
            """Name of the backend supporting cinder."""

        @dataclass
        class Neutron:
            """Information on the Neutron component.
            """
            ip_version: Optional[str] = None
            """TCP/IP protocol in use."""
            backend: Optional[str] = None
            """Name of the backend supporting neutron."""
            ml2_driver: Optional[str] = None
            """Comma delimited list with the name of the mechanism drivers."""
            tls_everywhere: Optional[str] = None
            """State (On / Off) of TLS-Everywhere."""

        cinder: Cinder = field(
            default_factory=lambda *_: DeploymentSummary.Components.Cinder()
        )
        """Section for the Cinder component."""
        neutron: Neutron = field(
            default_factory=lambda *_: DeploymentSummary.Components.Neutron()
        )
        """Section for the Neutron component."""

    release: Optional[str] = None
    """Name of the OpenStack release deployed."""
    infra_type: Optional[str] = None
    """Infrastructure type of the cloud."""
    topology: Optional[Topology] = None
    """Definition of the deployed network."""
    components: Components = field(
        default_factory=lambda *_: DeploymentSummary.Components()
    )
    """Section dedicated to each of the components that form the deployment."""
