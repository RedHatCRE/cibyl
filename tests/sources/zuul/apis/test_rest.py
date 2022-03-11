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
from unittest.mock import Mock

from cibyl.sources.zuul.apis.rest import (ZuulRESTClient, ZuulSession,
                                          ZuulTenantRESTClient)


class TestZuulSession(TestCase):
    """Tests for :class:`ZuulSession`.
    """

    def test_api_url(self):
        """Checks that the session correctly builds the API URL from the
        host's URL."""
        url = 'http://localhost:8080/zuul'

        session = ZuulSession(Mock(), url, None)

        self.assertEqual(f'{url}/api/', session.url)

    def test_happy_query(self):
        """Tests that the JSON from the response is returned if the query
        is successful."""
        url = 'http://localhost:8080/zuul'
        service = 'service'

        json = {
            'param_1': 'val_1',
            'param_2': 'val_2'
        }

        rest = Mock()
        rest.get = Mock()

        request = Mock()
        request.json = Mock()
        request.raise_for_status = Mock()

        rest.get.return_value = request

        request.json.return_value = json

        session = ZuulSession(rest, url, None)

        self.assertEqual(json, session.get(service))

        rest.get.assert_called_with(f'{session.url}{service}')

        request.raise_for_status.assert_called()
        request.json.assert_called()


class TestZuulTenantRESTClient(TestCase):
    """Tests for :class:`ZuulTenantRESTClient`.
    """

    def test_builds(self):
        """Tests call to 'builds' end-point.
        """
        tenant = {
            'name': 'tenant_1'
        }

        builds = [
            {
                'name': 'build_1'
            },
            {
                'name': 'build_2'
            }
        ]

        session = Mock()
        session.get = Mock()

        session.get.return_value = builds

        client = ZuulTenantRESTClient(session, tenant)

        self.assertEqual(builds, client.builds())

        session.get.assert_called_once_with(
            f"tenant/{tenant['name']}/builds"
        )

    def test_buildsets(self):
        """Tests call to 'buildsets' end-point.
        """
        tenant = {
            'name': 'tenant_1'
        }

        buildsets = [
            {
                'name': 'buildset_1'
            },
            {
                'name': 'buildset_2'
            }
        ]

        session = Mock()
        session.get = Mock()

        session.get.return_value = buildsets

        client = ZuulTenantRESTClient(session, tenant)

        self.assertEqual(buildsets, client.buildsets())

        session.get.assert_called_once_with(
            f"tenant/{tenant['name']}/buildsets"
        )

    def test_jobs(self):
        """Tests call to 'jobs' end-point.
        """
        tenant = {
            'name': 'tenant_1'
        }

        jobs = [
            {
                'name': 'job_1'
            },
            {
                'name': 'job_2'
            }
        ]

        session = Mock()
        session.get = Mock()

        session.get.return_value = jobs

        client = ZuulTenantRESTClient(session, tenant)

        self.assertEqual(jobs, client.jobs())

        session.get.assert_called_once_with(
            f"tenant/{tenant['name']}/jobs"
        )


class TestZuulRestClient(TestCase):
    """Tests for :class:`ZuulRESTClient`
    """

    def test_info(self):
        """Tests call to 'info' end-point.
        """
        info = {
            'hello': 'world'
        }

        session = Mock()
        session.get = Mock()

        session.get.return_value = info

        client = ZuulRESTClient(session)

        self.assertEqual(info, client.info())

        session.get.assert_called_once_with('info')

    def test_tenants(self):
        """Tests call to 'tenants' end-point.
        """
        tenants = [
            {
                'name': 'tenant_1'
            },
            {
                'name': 'tenant_2'
            }
        ]

        session = Mock()
        session.get = Mock()

        session.get.return_value = tenants

        client = ZuulRESTClient(session)

        for idx, tenant in enumerate(client.tenants()):
            self.assertEqual(tenants[idx]['name'], tenant.name)

        session.get.assert_called_once_with('tenants')
