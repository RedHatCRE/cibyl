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
from enum import Enum
from typing import Dict, Iterable, NamedTuple, Optional, Sequence

from tripleo import __path__ as tripleo_package_path
from tripleo.insights.exceptions import IllegibleData
from tripleo.insights.io import Topology
from tripleo.insights.topology import Node
from tripleo.utils.fs import File, cd_context_manager
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

        with cd_context_manager(tripleo_package_path[0]):
            # the default schemas path are stored in a path relative to the
            # root of the tripleo package. In case the working directory is
            # different, we want them to be reachable
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

    def __init__(
        self,
        data: YAML,
        schema: File = File('_data/schemas/environment.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    @property
    def keys(self) -> 'EnvironmentInterpreter.Keys':
        """
        :return: Knowledge that this has about the environment file's contents.
        """
        return self.Keys()

    def get_intra_type(self) -> Optional[str]:
        """
        :return: Value of the infrastructure type field. 'None' if the field
            is not present.
        """
        key = self.keys.infra_type

        for provider in (self.overrides, self.data):
            if key in provider:
                return provider[key]

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

    def __init__(
        self,
        data: YAML,
        schema: File = File('_data/schemas/featureset.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    @property
    def keys(self) -> 'FeatureSetInterpreter.Keys':
        """
        :return: Knowledge that this has about the featureset file's contents.
        """
        return self.Keys()

    def is_ipv6(self) -> bool:
        """
        :return: True if the deployment works under IPv6, False if it does
            under IPv4. If the field is not present, then IPv4 is assumed.
        """
        key = self.keys.ipv6

        for provider in (self.overrides, self.data):
            if key in provider:
                return provider[key]

        return False

    def is_tls_everywhere_enabled(self) -> bool:
        """
        :return: True if the deployment uses tls everywhere, False if it does
            not. If the field is not present, then False is returned too.
        """
        key = self.keys.tls_everywhere

        for provider in (self.overrides, self.data):
            if key in provider:
                return provider[key]

        return False

    def get_scenario(self) -> Optional[str]:
        """
        :return: Name of the scenario file that complements this featureset.
            'None' if it is not defined.
        """
        key = self.keys.scenario

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

        class Root(NamedTuple):
            """Defines the keys found at the file's root.
            """
            overcloud: str = 'overcloud_nodes'
            """Section giving an outline of the to be deployed cloud."""
            topology: str = 'topology_map'
            """Section providing configuration on the to be deployed cloud."""

        class OvercloudNodes(NamedTuple):
            """Keys found in the 'overcloud_nodes' section.
            """

            class NodeFlavor(str, Enum):
                """Values of the 'flavor' key that describe the node type.
                """
                CONTROL = 'control'
                COMPUTE = 'compute'
                CEPH = 'ceph'

            name: str = 'name'
            """Name of the node."""
            flavor: str = 'flavor'
            """Type of the node."""

        class TopologyMap(NamedTuple):
            """Keys found in the 'topology_map' section.
            """
            # Keys to node types
            compute: str = 'Compute'
            """Contains data on compute nodes."""
            controller: str = 'Controller'
            """Contains data on controller nodes."""
            ceph: str = 'CephStorage'
            """Contains data on ceph nodes."""
            cell: str = 'CellController'
            """Contains data on cell nodes."""

            # Keys inside each node type
            scale: str = 'scale'
            """Number of nodes of a certain type."""

        root: Root = Root()
        """Keys at the file's root."""
        overcloud_node: OvercloudNodes = OvercloudNodes()
        """Keys at the 'overcloud_node' section."""
        topology_map: TopologyMap = TopologyMap()
        """Keys at the 'topology_map' section."""

    def __init__(
        self,
        data: YAML,
        schema: File = File('_data/schemas/nodes.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    @property
    def keys(self) -> 'NodesInterpreter.Keys':
        """
        :return: Knowledge that this has about the nodes file's contents.
        """
        return self.Keys()

    def get_topology(self) -> Optional[Topology]:
        """
        :return: Information on the topology described by the file. 'None'
            if not enough information is present on the file.
        """
        key = self.keys.root.overcloud

        for provider in (self.overrides, self.data):
            if key in provider:
                return self._new_topology_from(provider[key])

        return None

    def _new_topology_from(self, overcloud_nodes: Iterable[dict]) -> Topology:
        keys = self.keys.overcloud_node
        flavors = self.keys.overcloud_node.NodeFlavor

        controller_nodes = []
        compute_nodes = []
        ceph_nodes = []

        for node in overcloud_nodes:
            name = node[keys.name]
            flavor = node[keys.flavor]

            if flavor == flavors.CONTROL:
                controller_nodes.append(Node(name))
                continue

            if flavor == flavors.COMPUTE:
                compute_nodes.append(Node(name))
                continue

            if flavor == flavors.CEPH:
                ceph_nodes.append(Node(name))
                continue

        return Topology(
            nodes=Topology.Nodes(
                controller=controller_nodes,
                compute=compute_nodes,
                ceph=ceph_nodes
            )
        )


class ReleaseInterpreter(FileInterpreter):
    """Takes care of making sense out of the contents of a release file.
    """

    class Keys(NamedTuple):
        """Defines the fields of interest contained by a release file.
        """
        release: str = 'release'
        """Field that holds the release name."""

    def __init__(
        self,
        data: YAML,
        schema: File = File('_data/schemas/release.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    @property
    def keys(self) -> 'ReleaseInterpreter.Keys':
        """
        :return: Knowledge that this has about the release file's contents.
        """
        return self.Keys()

    def get_release_name(self) -> Optional[str]:
        """
        :return: Name of the release, for example: 'wallaby'. None if the
            field is not present.
        """
        key = self.keys.release

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
            """Key pointing to the tenant network type."""
            ml2_driver: str = 'NeutronMechanismDrivers'
            """Key pointing to the mechanism drivers for the tenant network."""

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

            :param keys: Set of keys that this will map.
            """
            self._keys = keys

        @property
        def keys(self) -> 'ScenarioInterpreter.Keys':
            """
            :return: Set of keys that this will map.
            """
            return self._keys

        @property
        def cinder_backends(self) -> Dict[str, str]:
            """
            :return: A map that matches each of the cinder backend keys to
                simple representation of the backend. For example:
                'CinderEnableIscsiBackend' -> 'iscsi'.
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

        These values are set to be the same as in the heat templates
        repository.
        """
        cinder_backend: str = 'iscsi'
        """Default backend supporting cinder."""
        neutron_backend: str = 'geneve'
        """Default backend supporting neutron."""
        ml2_driver: str = 'ovn'
        """Default ml2 driver."""

    def __init__(
        self,
        data: YAML,
        schema: File = File('_data/schemas/scenario.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    @property
    def keys(self) -> 'ScenarioInterpreter.Keys':
        """
        :return: Knowledge this has on the scenario file.
        """
        return self.Keys()

    @property
    def mappings(self) -> 'ScenarioInterpreter.Mappings':
        """
        :return: Output for each of the keys.
        """
        return self.Mappings(self.keys)

    @property
    def defaults(self) -> 'ScenarioInterpreter.Defaults':
        """
        :return: Values returned by the interpreter when wanted data
            is not present.
        """
        return self.Defaults()

    @property
    def _parameters(self) -> dict:
        """
        :return: Contents of the 'parameter_defaults' section. Empty if it
            is not present.
        """
        return self.data.get(self.keys.parameters, {})

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
            keys = self.keys.cinder.backends

            result = []

            # Iterate over all known backends
            for key in keys:
                # Is the backend present on the file?
                if key in self._parameters:
                    # Is it set to true then?
                    if self._parameters[key]:
                        result.append(key)

            return result

        mapping = self.mappings.cinder_backends
        default = self.defaults.cinder_backend

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
        key = self.keys.neutron.backend
        default = self.defaults.neutron_backend

        if key not in self._parameters:
            # The backend is not defined on the file
            return default

        return self._parameters[key]

    def get_ml2_driver(self) -> str:
        """
        :return: Comma delimited list with the names of the ml2 drivers
            configured for Neutron. If none are defined, then this will fall
            back to OVN.
        """
        key = self.keys.neutron.ml2_driver
        default = self.defaults.ml2_driver

        if key not in self._parameters:
            # The drivers are not defined on the file
            return default

        return self._parameters[key]
