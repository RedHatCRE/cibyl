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
from unittest import TestCase

from cibyl.cli.query import QueryType, get_query_type
from tests.cibyl.utils import OpenstackPluginWithJobSystem


class TestGetQueryType(TestCase):
    """Tests for :func:`get_query_type`.
    """

    def test_get_none(self):
        """Checks that "None" is returned if no argument is passed.
        """
        args = {
        }

        self.assertEqual(QueryType.NONE, get_query_type(**args))

    def test_get_tenant(self):
        """Checks that "Tenants" is returned for "--tenants".
        """
        args = {
            'tenants': None
        }

        self.assertEqual(QueryType.TENANTS, get_query_type(**args))

    def test_get_projects(self):
        """Checks that "Projects" is returned for "--projects".
        """
        args = {
            'projects': None
        }

        self.assertEqual(QueryType.PROJECTS, get_query_type(**args))

    def test_get_pipelines(self):
        """Checks that "Pipelines" is returned for "--pipelines".
        """
        args = {
            'pipelines': None
        }

        self.assertEqual(QueryType.PIPELINES, get_query_type(**args))

    def test_get_jobs(self):
        """Checks that "Jobs" is returned for "--jobs".
        """
        args = {
            'jobs': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_builds(self):
        """Checks that "Builds" is returned for "--builds".
        """
        args = {
            'builds': None
        }

        self.assertEqual(QueryType.BUILDS, get_query_type(**args))

    def test_get_last_builds(self):
        """Checks that "Builds" is returned for "--last-builds".
        """
        args = {
            'last_build': None
        }

        self.assertEqual(QueryType.BUILDS, get_query_type(**args))

    def test_get_build_status(self):
        """Checks that "Builds" is returned for "--build-status".
        """
        args = {
            'build_status': None
        }

        self.assertEqual(QueryType.BUILDS, get_query_type(**args))

    def test_get_tests(self):
        """Checks that "Tests" is returned for "--tests".
        """
        args = {
            'tests': None
        }

        self.assertEqual(QueryType.TESTS, get_query_type(**args))

    def test_get_test_duration(self):
        """Checks that "Tests" is returned for "--test-duration".
        """
        args = {
            'test_duration': None
        }

        self.assertEqual(QueryType.TESTS, get_query_type(**args))

    def test_get_test_result(self):
        """Checks that "Tests" is returned for "--test-result".
        """
        args = {
            'test_result': None
        }

        self.assertEqual(QueryType.TESTS, get_query_type(**args))

    def test_get_variants(self):
        """Checks that "Jobs" is returned for "--variants"."""
        args = {
            'variants': None
        }

        self.assertEqual(QueryType.VARIANTS, get_query_type(**args))

    def test_get_ip_version(self):
        """Checks that "None" is returned for "--ip-version" if the openstack
        plugin is not added."""
        args = {
            'ip_version': None
        }

        self.assertEqual(QueryType.NONE, get_query_type(**args))

    def test_get_feature(self):
        """Checks that "FEATURES" is returned for "--feature"."""
        args = {}

        self.assertEqual(QueryType.FEATURES,
                         get_query_type(command="features", **args))

    def test_get_feature_no_command(self):
        """Checks that "FEATURES" is returned for "--feature" without the
        command argument."""
        args = {}

        self.assertEqual(QueryType.NONE, get_query_type(**args))

    def test_get_feature_jobs(self):
        """Checks that "FEATURES_JOBS" is returned for "--feature" and
        "--jobs"."""
        args = {
            'jobs': None
        }

        query = get_query_type(command="features", **args)
        self.assertIn(QueryType.FEATURES, query)
        self.assertIn(QueryType.JOBS, query)

    def test_get_feature_jobs_no_command(self):
        """Checks that "JOBS" is returned for "--feature" and
        "--jobs" without the command argument."""
        args = {
            'jobs': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_tests_builds(self):
        """Checks that "Tests" is returned for "--tests" and "--last-build".
        """
        args = {
            'tests': None,
            'last_build': None
        }

        self.assertIn(QueryType.TESTS, get_query_type(**args))


class TestGetQueryTypeOpenstackPlugin(OpenstackPluginWithJobSystem):
    """Tests for :func:`get_query_type` with the openstack plugin loaded."""

    def test_get_release(self):
        """Checks that "Jobs" is returned for "--release" if the openstack
        plugin is added."""
        args = {
            'release': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_spec(self):
        """Checks that "Jobs" is returned for "--spec" if the openstack
        plugin is added."""
        args = {
            'spec': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_infra_type(self):
        """Checks that "Jobs" is returned for "--infra-type" if the openstack
        plugin is added."""
        args = {
            'infra_type': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_nodes(self):
        """Checks that "Jobs" is returned for "--nodes" if the openstack
        plugin is added."""
        args = {
            'nodes': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_controllers(self):
        """Checks that "Jobs" is returned for "--controllers" if the openstack
        plugin is added."""
        args = {
            'controllers': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_computes(self):
        """Checks that "Jobs" is returned for "--computes" if the openstack
        plugin is added."""
        args = {
            'computes': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_services(self):
        """Checks that "Jobs" is returned for "--services" if the openstack
        plugin is added."""
        args = {
            'services': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_ip_version(self):
        """Checks that "Jobs" is returned for "--ip-version" if the openstack
        plugin is added."""
        args = {
            'ip_version': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_topology(self):
        """Checks that "Jobs" is returned for "--topology" if the openstack
        plugin is added."""
        args = {
            'topology': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_dvr(self):
        """Checks that "Jobs" is returned for "--dvr" if the openstack
        plugin is added."""
        args = {
            'dvr': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_ml2_driver(self):
        """Checks that "Jobs" is returned for "--ml2-driver" if the openstack
        plugin is added."""
        args = {
            'ml2_driver': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_tls_everywhere(self):
        """Checks that "Jobs" is returned for "--tls-everywhere" if the
        openstack plugin is added.
        """
        args = {
            'tls_everywhere': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_ironic_inspector(self):
        """Checks that "Jobs" is returned for "--ironic-inspector" if the
        openstack plugin is added.
        """
        args = {
            'ironic_inspector': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_network_backend(self):
        """Checks that "Jobs" is returned for "--network-backend" if the
        openstack plugin is added.
        """
        args = {
            'network_backend': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_cinder_backend(self):
        """Checks that "Jobs" is returned for "--storage-backend" if the
        openstack plugin is added.
        """
        args = {
            'cinder_backend': None
        }

        self.assertEqual(QueryType.JOBS, get_query_type(**args))

    def test_get_spec_tenants(self):
        """Checks that "Jobs" is returned for "--storage-backend" if the
        openstack plugin is added and is run in combination of arguments like
        --tenants.
        """
        args = {
            'tenants': None,
            'cinder_backend': None
        }

        self.assertIn(QueryType.JOBS, get_query_type(**args))

    def test_get_spec_packages(self):
        """Checks that "Jobs" is returned for "--packages" if the
        openstack plugin is added and is run in combination of arguments like
        --tenants.
        """
        args = {
            'tenants': None,
            'packages': None
        }

        self.assertIn(QueryType.JOBS, get_query_type(**args))

    def test_get_spec_services(self):
        """Checks that "Jobs" is returned for "--services" if the
        openstack plugin is added and is run in combination of arguments like
        --tenants.
        """
        args = {
            'tenants': None,
            'services': None
        }

        self.assertIn(QueryType.JOBS, get_query_type(**args))

    def test_get_spec_containers(self):
        """Checks that "Jobs" is returned for "--containers" if the
        openstack plugin is added and is run in combination of arguments like
        --tenants.
        """
        args = {
            'tenants': None,
            'containers': None
        }

        self.assertIn(QueryType.JOBS, get_query_type(**args))
