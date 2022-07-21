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
from typing import Dict, NamedTuple, Optional, Sequence

from tripleo.insights.exceptions import IllegibleData
from tripleo.insights.io import Topology
from tripleo.utils.fs import File
from tripleo.utils.json import Draft7ValidatorFactory, JSONValidatorFactory
from tripleo.utils.yaml import YAML


class FileInterpreter(ABC):
    """Base class for all interpreters that take care of giving meaning to
    the contents of the files that outline a deployment.
    """

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

        def validate_data(instance):
            if not validator.is_valid(instance):
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

    class Keys(NamedTuple):
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
        :return: Value of the infrastructure type field. 'None' if the field
            is not present.
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

    class Keys(NamedTuple):
        """Defines the fields of interest contained by a featureset file.
        """
        ipv6: str = 'overcloud_ipv6'
        """Indicates IP version of deployment."""
        scenario: str = 'composable_scenario'
        """Indicates the scenario of this deployment."""
        tls_everywhere: str = 'enable_tls_everywhere'
        """Indicates whether TLS everywhere is enabled."""

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
            under IPv4. If the field is not present, then IPv4 is assumed.
        """
        key = self.KEYS.ipv6

        for provider in (self.overrides, self.data):
            if key in provider:
                return provider[key]

        return False

    def is_tls_everywhere_enabled(self) -> bool:
        """
        :return: True if the deployment uses tls everywhere, False if it does
            not. If the field is not present, then False is returned too.
        """
        key = self.KEYS.tls_everywhere

        for provider in (self.overrides, self.data):
            if key in provider:
                return provider[key]

        return False

    def get_scenario(self) -> Optional[str]:
        """
        :return: Name of the scenario file that complements this featureset.
            'None' if it is not defined.
        """
        key = self.KEYS.scenario

        for provider in (self.overrides, self.data):
            if key in provider:
                return provider[key]

        return None


class NodesInterpreter(FileInterpreter):
    """Takes care of making sense out of the contents of a nodes file.
    """

    class Keys(NamedTuple):
        """Defines the fields of interest contained by a nodes file.
        """
        # Root level
        topology: str = 'topology_map'
        """Field that defines the deployment's topology."""

        # 'topology_map' level
        compute: str = 'Compute'
        """Contains data on compute nodes."""
        controller: str = 'Controller'
        """Contains data on controller nodes."""
        ceph: str = 'CephStorage'
        """Contains data on ceph nodes."""
        cell: str = 'CellController'
        """Contains data on cell nodes."""

        # 'node' level
        scale: str = 'scale'
        """Number of nodes of a certain type."""

    KEYS = Keys()
    """Knowledge that this has about the nodes file's contents."""

    def __init__(
        self,
        data: YAML,
        schema: File = File('tripleo/_data/schemas/nodes.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    def get_topology(self) -> Optional[Topology]:
        """
        :return: Information on the topology described by the file. 'None'
            if not enough information is present on the file.
        """
        key = self.KEYS.topology

        for provider in (self.overrides, self.data):
            if key in provider:
                return self._new_topology_from(provider[key])

        return None

    def _new_topology_from(self, topology_map: dict) -> Topology:
        """
        :param topology_map: Take a look at the 'topology_map' level on the
            'Keys' dictionary for the set of keys expected on this dictionary.
        """
        result = Topology()

        keys = self.KEYS

        if keys.compute in topology_map:
            result.compute = topology_map[keys.compute][keys.scale]

        if keys.controller in topology_map:
            result.controller = topology_map[keys.controller][keys.scale]

        if keys.ceph in topology_map:
            result.ceph = topology_map[keys.ceph][keys.scale]

        if keys.cell in topology_map:
            result.cell = topology_map[keys.cell][keys.scale]

        return result


class ReleaseInterpreter(FileInterpreter):
    """Takes care of making sense out of the contents of a release file.
    """

    class Keys(NamedTuple):
        """Defines the fields of interest contained by a release file.
        """
        release: str = 'release'
        """Field that holds the release name."""

    KEYS = Keys()
    """Knowledge that this has about the release file's contents."""

    def __init__(
        self,
        data: YAML,
        schema: File = File('tripleo/_data/schemas/release.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    def get_release_name(self) -> Optional[str]:
        """
        :return: Name of the release, for example: 'wallaby'. None if the
            field is not present.
        """
        key = self.KEYS.release

        for provider in (self.overrides, self.data):
            if key in provider:
                return provider[key]

        return None


class ScenarioInterpreter(FileInterpreter):
    """Takes care of making sense out of the contents of a scenario file.
    """

    class Keys(NamedTuple):
        """Defines the fields of interest in the scenario.
        """

        class Cinder(NamedTuple):
            """Defines all the fields related to the cinder component.
            """

            class Backends(NamedTuple):
                """Defines all the fields related to the cinder backend.
                """
                powerflex: str = 'CinderEnablePowerFlexBackend'
                powermax: str = 'CinderEnablePowermaxBackend'
                powerstore: str = 'CinderEnablePowerStoreBackend'
                sc: str = 'CinderEnableScBackend'
                dell_emc_unity: str = 'CinderEnableDellEMCUnityBackend'
                dell_emc_vnx: str = 'CinderEnableDellEMCVNXBackend'
                dell_sc: str = 'CinderEnableDellScBackend'
                xtremio: str = 'CinderEnableXtremioBackend'
                netapp: str = 'CinderEnableNetappBackend'
                pure: str = 'CinderEnablePureBackend'
                iscsi: str = 'CinderEnableIscsiBackend'
                nfs: str = 'CinderEnableNfsBackend'
                rbd: str = 'CinderEnableRbdBackend'

            backends = Backends()
            """Keys pointing to the component's backend."""

        class Neutron(NamedTuple):
            """Defines all the fields related to the neutron component.
            """
            backend: str = 'NeutronNetworkType'
            """Keys pointing to the tenant network type."""

        parameters: str = 'parameter_defaults'
        """Level at which the parameters are defined."""

        cinder: Cinder = Cinder()
        """Keys related to the cinder component."""
        neutron: Neutron = Neutron()
        """Keys related to the neutron component."""

    class Mappings:
        """Maps keys on the scenario file to an output.
        """

        def __init__(self, keys: 'ScenarioInterpreter.Keys'):
            """Constructor.

            :param keys: The keys to map.
            """
            self._keys = keys

        @property
        def keys(self) -> 'ScenarioInterpreter.Keys':
            """
            :return: The keys this will map.
            """
            return self._keys

        @property
        def cinder_backends(self) -> Dict[str, str]:
            """
            :return: A map that relates each of the cinder backend keys to
                an output word. For example: CinderEnableIscsiBackend -> iscsi
            """
            return {
                self.keys.cinder.backends.powerflex: 'powerflex',
                self.keys.cinder.backends.powermax: 'powermax',
                self.keys.cinder.backends.powerstore: 'powerstore',
                self.keys.cinder.backends.sc: 'sc',
                self.keys.cinder.backends.dell_emc_unity: 'dell-emc unity',
                self.keys.cinder.backends.dell_emc_vnx: 'dell-emc vnx',
                self.keys.cinder.backends.dell_sc: 'dell sc',
                self.keys.cinder.backends.xtremio: 'xtremio',
                self.keys.cinder.backends.netapp: 'netapp',
                self.keys.cinder.backends.pure: 'pure',
                self.keys.cinder.backends.iscsi: 'iscsi',
                self.keys.cinder.backends.nfs: 'nfs',
                self.keys.cinder.backends.rbd: 'rbd'
            }

    class Defaults(NamedTuple):
        """Defines the values returned by the interpreter when it cannot
        find the data on the scenario file.

        These values default themselves to the ones defined on the heat
        templates repository.
        """
        cinder_backend: str = 'iscsi'
        """Default backend supporting cinder."""
        neutron_backend: str = 'geneve'
        """Default backend supporting neutron."""

    KEYS = Keys()
    """Knowledge this has on the scenario file."""
    MAPPINGS = Mappings(KEYS)
    """Output for each of the keys."""
    DEFAULTS = Defaults()
    """Values returned by the interpreter when wanted data is not present."""

    def __init__(
        self,
        data: YAML,
        schema: File = File('tripleo/_data/schemas/scenario.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    @property
    def _parameters(self) -> dict:
        """
        :return: Contents of the 'parameter_defaults' section. Empty if it
            is not present.
        """
        return self.data.get(self.KEYS.parameters, {})

    def get_cinder_backend(self) -> str:
        """
        :return: Name of the backend behind Cinder. If none is defined,
            this will default to ISCSI.
        :raises IllegibleData: If more than one backend is defined on the
            scenario.
        """

        def get_backends() -> Sequence[str]:
            """
            :return: Keys to all the backends that are set to True on the
                scenario.
            """
            keys = self.KEYS.cinder.backends

            result = []

            # Iterate over all known backends
            for key in keys:
                # Is the backend present on the file?
                if key in self._parameters:
                    # Is it set to true then?
                    if self._parameters[key]:
                        result.append(key)

            return result

        mapping = self.MAPPINGS.cinder_backends
        default = self.DEFAULTS.cinder_backend

        backends = get_backends()

        if len(backends) == 0:
            # No backends are defined on the file
            return default

        if len(backends) != 1:
            raise IllegibleData(
                'More than one Cinder backend available. '
                'Cannot determine which one to pick.'
            )

        backend = backends[0]

        return mapping[backend]

    def get_neutron_backend(self) -> str:
        """
        :return: Name of the backend behind Neutron. If none is defined,
            then this will fall back to Geneve.
        """
        key = self.KEYS.neutron.backend
        default = self.DEFAULTS.neutron_backend

        if key not in self._parameters:
            # The backend is not defined on the file
            return default

        return self._parameters[key]
