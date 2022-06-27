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
from tripleo.utils.types import URL, Path

DEFAULT_REPOSITORY: URL = 'https://github.com/openstack/tripleo-quickstart.git'

DEFAULT_ENVIRONMENT_FILE: Path = 'config/environments/default_libvirt.yml'
DEFAULT_FEATURESET_FILE: Path = 'config/general_config/minimal.yml'
DEFAULT_NODES_FILE: Path = 'config/nodes/1ctlr_1comp.yml'
DEFAULT_RELEASE_FILE: Path = 'config/release/master.yml'
