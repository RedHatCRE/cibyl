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
from abc import ABC
from string import Template

from dataclasses import dataclass
from typing import Dict, Optional

from tripleo.insights.exceptions import IllegibleData
from tripleo.utils.fs import File
from tripleo.utils.json import Draft7ValidatorFactory, JSONValidatorFactory
from tripleo.utils.yaml import YAML


class FileInterpreter(ABC):
    def __init__(
        self,
        data: YAML,
        schema: File,
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        """Constructor.

        :param data: Contents of the file, parsed from YAML format.
        :param schema: The structure that the file must follow.
        :param overrides: Dictionary of fields that override those from the
            file. If the interpreter finds a field both on the file and in
            here, it will choose this one over the other. Leave as None is you
            want to stick to data from the file.
        :param validator_factory: Creates the validator used to check the
            data against the schema.
        :raises IOError: If the schema file does not exist or cannot be opened.
        :raises IllegibleData:
            If the data does not match the schema.
            If the 'overrides' dictionary does not match the schema.
        """

        def validate_data(__data):
            if not validator.is_valid(__data):
                raise IllegibleData('Data does not conform to its schema.')

        if overrides is None:
            overrides = {}

        validator = validator_factory.from_file(schema)

        validate_data(data)
        validate_data(overrides)

        self._data = data
        self._overrides = overrides

    @property
    def data(self) -> YAML:
        """
        :return: Raw data contained by the file.
        """
        return self._data

    @property
    def overrides(self) -> Dict:
        """
        :return: Collection of fields that will override the data from the
            file.
        """
        return self._overrides


class EnvironmentInterpreter(FileInterpreter):
    """Takes care of making sense out of the contents of an environment file.
    """

    @dataclass
    class Keys:
        """Defines the fields of interest contained by an environment file.
        """
        infra_type: str = 'environment_type'
        """Field that holds the cloud's infrastructure type."""

    KEYS = Keys()
    """Knowledge that this has about the environment file's contents."""

    def __init__(
        self,
        data: YAML,
        schema: File = File('tripleo/_data/schemas/environment.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    def get_intra_type(self) -> Optional[str]:
        """
        :return: Value of the infrastructure type field, None if the field
            in not present.
        """
        key = self.KEYS.infra_type

        if key in self.overrides:
            return self.overrides[key]

        if key in self.data:
            return self.data[key]

        return None


class FeatureSetInterpreter(FileInterpreter):
    """Takes care of making sense out of the contents of a featureset file.
    """

    @dataclass
    class Keys:
        """Defines the fields of interest contained by a featureset file.
        """
        ipv6: str = 'overcloud_ipv6'
        """Indicates IP version of deployment."""

    KEYS = Keys()
    """Knowledge that this has about the featureset file's contents."""

    def __init__(
        self,
        data: YAML,
        schema: File = File('tripleo/_data/schemas/featureset.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    def is_ipv6(self) -> bool:
        """
        :return: True if the deployment works under IPv6, False if it does
            under IPv4.
        """
        key = self.KEYS.ipv6

        if key in self.overrides:
            return self.overrides[key]

        if key in self.data:
            return self.data[key]

        return False


class NodesInterpreter(FileInterpreter):
    @dataclass
    class Keys:
        topology: str = 'topology_map'

    @dataclass
    class Topology:
        compute: int = 0
        ctrl: int = 0
        ceph: int = 0

        to_str_tmpl: Template = Template(
            'compute:$compute,controller:$ctrl,ceph:$ceph'
        )

        def __str__(self):
            return self.to_str_tmpl.substitute(
                compute=self.compute,
                ctrl=self.ctrl,
                ceph=self.ceph
            )

    KEYS = Keys()

    def __init__(
        self,
        data: YAML,
        schema: File = File('tripleo/_data/schemas/nodes.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    def get_topology(self) -> Optional[Topology]:
        def build_topology(data):
            result = NodesInterpreter.Topology()

            ctrl_key = 'Controller'
            compute_key = 'Compute'
            ceph_key = 'CephStorage'

            scale_key = 'scale'

            if ctrl_key in data:
                result.ctrl = data[ctrl_key][scale_key]

            if compute_key in data:
                result.compute = data[compute_key][scale_key]

            if ceph_key in data:
                result.ceph = data[ceph_key][scale_key]

            return result

        key = self.KEYS.topology

        for provider in (self.overrides, self.data):
            if key in provider:
                return build_topology(provider[key])

        return None
