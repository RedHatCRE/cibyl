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


class ArgumentReview:
    """Interpreter for arguments coming from the CLI. This class takes care
    of analyzing them and figuring out what the user is asking for.
    """

    def is_tenants_query_requested(self, **kwargs) -> bool:
        """
        :param kwargs: Arguments from the CLI.
        :return: True is the user asked for tenants, False if not.
        """
        return any(
            arg in kwargs
            for arg in ('tenants',)
        )

    def is_projects_query_requested(self, **kwargs) -> bool:
        """
        :param kwargs: Arguments from the CLI.
        :return: True is the user asked for projects, False if not.
        """
        return any(
            arg in kwargs
            for arg in ('projects',)
        )

    def is_pipelines_query_requested(self, **kwargs) -> bool:
        """
        :param kwargs: Arguments from the CLI.
        :return: True is the user asked for pipelines, False if not.
        """
        return any(
            arg in kwargs
            for arg in ('pipelines',)
        )

    def is_jobs_query_requested(self, **kwargs) -> bool:
        """
        :param kwargs: Arguments from the CLI.
        :return: True is the user asked for jobs, False if not.
        """
        return any(
            arg in kwargs
            for arg in ('jobs', 'job_url')
        )

    def is_variants_query_requested(self, **kwargs) -> bool:
        """
        :param kwargs: Arguments from the CLI.
        :return: True is the user asked for variants, False if not.
        """
        return any(
            arg in kwargs
            for arg in ('variants',)
        )

    def is_builds_query_requested(self, **kwargs) -> bool:
        """
        :param kwargs: Arguments from the CLI.
        :return: True is the user asked for builds, False if not.
        """
        return any(
            arg in kwargs
            for arg in ('builds', 'last_build', 'build_status')
        )

    def is_tests_query_requested(self, **kwargs) -> bool:
        """
        :param kwargs: Arguments from the CLI.
        :return: True is the user asked for tests, False if not.
        """
        return any(
            arg in kwargs
            for arg in ('tests', 'test_result', 'test_duration')
        )
