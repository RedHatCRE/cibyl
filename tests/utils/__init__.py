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
from copy import deepcopy
from unittest import TestCase

from cibyl import features
from cibyl.cli.query import QuerySelector
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.base.system import JobsSystem, System
from cibyl.models.ci.zuul.job import Job as ZuulJob
from cibyl.models.ci.zuul.system import ZuulSystem
from cibyl.plugins import enable_plugins


class RestoreAPIs(TestCase):
    """Setup a test class that can restore the modification applied to System
    and Job APIs."""

    @classmethod
    def setUpClass(cls):
        """Setup the API of system using that of JobsSystem."""
        cls.original_job_api = deepcopy(Job.API)
        cls.original_zuul_job_api = deepcopy(ZuulJob.API)
        cls.original_system_api = deepcopy(System.API)
        cls.plugin_attributes = deepcopy(Job.plugin_attributes)
        cls.feature_paths = deepcopy(features.features_locations)

    @classmethod
    def tearDownClass(cls):
        """Restore the original APIs of Job and System to avoid interferring
        with other systems."""
        Job.API = deepcopy(cls.original_job_api)
        Job.plugin_attributes = deepcopy(cls.plugin_attributes)
        ZuulJob.API = deepcopy(cls.original_zuul_job_api)
        System.API = deepcopy(cls.original_system_api)
        QuerySelector.query_selector_functions = []
        features.features_locations = deepcopy(cls.feature_paths)


class JobSystemAPI(RestoreAPIs):
    """Setup a test class that applies the JobSystemAPI and Job APIs."""

    @classmethod
    def setUpClass(cls):
        """Setup the API of system using that of JobsSystem and apply the
        openstack plugin."""
        super().setUpClass()
        System.API = deepcopy(JobsSystem.API)


class ZuulSystemAPI(RestoreAPIs):
    """Setup a test class that applies the ZuulSystemAPI."""

    @classmethod
    def setUpClass(cls):
        """Setup the API of system using that of ZuulSystem."""
        super().setUpClass()
        System.API = deepcopy(ZuulSystem.API)


class OpenstackPluginWithJobSystem(JobSystemAPI):
    """Setup a test class to test environments with a JobsSystem and Openstack
    plugin."""

    @classmethod
    def setUpClass(cls):
        """Setup the API of system using that of JobsSystem and apply the
        openstack plugin."""
        super().setUpClass()
        enable_plugins(["openstack"])

    @classmethod
    def tearDownClass(cls):
        """Restore the original APIs of Job and System to avoid interferring
        with other systems."""
        super().tearDownClass()


class OpenstackPluginWithZuulSystem(ZuulSystemAPI):
    """Setup a test class to test environments with a ZuulSystem and Openstack
    plugin."""

    @classmethod
    def setUpClass(cls):
        """Setup the API of system using that of ZuulSystem and apply the
        openstack plugin."""
        super().setUpClass()
        enable_plugins(["openstack"])

    @classmethod
    def tearDownClass(cls):
        """Restore the original APIs of Job and System to avoid interferring
        with other systems."""
        super().tearDownClass()
