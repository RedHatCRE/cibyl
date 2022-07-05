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

from tripleo.insights.defaults import (DEFAULT_ENVIRONMENT_FILE,
                                       DEFAULT_FEATURESET_FILE,
                                       DEFAULT_NODES_FILE, DEFAULT_QUICKSTART,
                                       DEFAULT_RELEASE_FILE, DEFAULT_THT)
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


@dataclass
class DeploymentSummary:
    """Defines the deployment that TripleO will perform based on the
    outline provided as input.
    """
    ip_version: str = 'N/A'
    """Name of the IP protocol used on the deployment."""
    infra_type: str = 'N/A'
    """Infrastructure type of the cloud."""
