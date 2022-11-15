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
from unittest.mock import MagicMock, Mock

from cibyl.sources.zuuld.backends.aggr import AggregatedBackend
from cibyl.sources.zuuld.errors import ZuulDError


class TestGet(TestCase):
    """Tests for :class:`AggregatedBackend.Get`.
    """

    def test_gets_from_first_backend_on_jobs(self):
        """Checks that the result from the first backend is returned if it
        does not fail.
        """
        spec = Mock()

        backend1 = Mock()
        backend1.jobs = MagicMock()
        backend2 = Mock()
        backend2.jobs = MagicMock()

        get = AggregatedBackend.Get(
            backends=[
                backend1,
                backend2
            ]
        )

        result = get.jobs(spec)

        self.assertEqual(backend1.jobs.return_value, result)

        backend1.jobs.assert_called_once_with(spec)
        backend2.jobs.assert_not_called()

    def test_skips_failed_backend_on_jobs(self):
        """Checks that if a backend fails while looking for jobs, the next
        one is tried.
        """

        def error():
            raise ZuulDError()

        spec = Mock()

        backend1 = Mock()
        backend1.jobs = Mock()
        backend1.jobs.side_effect = lambda *_: error()
        backend2 = Mock()
        backend2.jobs = MagicMock()

        get = AggregatedBackend.Get(
            backends=[
                backend1,
                backend2
            ]
        )

        result = get.jobs(spec)

        self.assertEqual(backend2.jobs.return_value, result)

        backend1.jobs.assert_called_once_with(spec)
        backend2.jobs.assert_called_once_with(spec)

    def test_error_if_all_fail_on_jobs(self):
        """Checks that if all backends fail while getting the jobs, an error
         is raised.
        """

        def error():
            raise ZuulDError()

        spec = Mock()

        backend1 = Mock()
        backend1.jobs = Mock()
        backend1.jobs.side_effect = lambda *_: error()
        backend2 = Mock()
        backend2.jobs = Mock()
        backend2.jobs.side_effect = lambda *_: error()

        get = AggregatedBackend.Get(
            backends=[
                backend1,
                backend2
            ]
        )

        with self.assertRaises(ZuulDError):
            get.jobs(spec)

        backend1.jobs.assert_called_once_with(spec)
        backend2.jobs.assert_called_once_with(spec)
