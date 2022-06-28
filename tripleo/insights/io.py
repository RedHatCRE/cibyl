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
from dataclasses import dataclass

from tripleo.insights.defaults import (DEFAULT_ENVIRONMENT_FILE,
                                       DEFAULT_FEATURESET_FILE, DEFAULT_HEAT,
                                       DEFAULT_NODES_FILE, DEFAULT_QUICKSTART,
                                       DEFAULT_RELEASE_FILE)
from tripleo.insights.types import URL, Path


@dataclass
class DeploymentOutline:
    quickstart: URL = DEFAULT_QUICKSTART
    heat: URL = DEFAULT_HEAT

    environment: Path = DEFAULT_ENVIRONMENT_FILE
    featureset: Path = DEFAULT_FEATURESET_FILE
    nodes: Path = DEFAULT_NODES_FILE
    release: Path = DEFAULT_RELEASE_FILE


@dataclass
class DeploymentSummary:
    ip_version: str
