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
import dateutil.parser

from cibyl.models.ci.zuul.tests.ansible import AnsibleTestStatus
from cibyl.sources.zuul.apis.tests.ansible.types import (AnsibleTest,
                                                         AnsibleTestHost)
from cibyl.sources.zuul.apis.tests.types import TestSuite
from cibyl.utils.json import Draft7ValidatorFactory, JSONValidatorFactory


class AnsibleTestParser:
    class TestArgs:
        DEFAULT_TEST_SCHEMA = 'data/json/schemas/zuul/ansible_test.json'

        schema: str = DEFAULT_TEST_SCHEMA
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()

    def __init__(self, test_args=TestArgs()):
        self._test_schema = test_args.schema
        self._test_validator_factory = test_args.validator_factory

    def parse(self, data):
        """

        :param data:
        :type data: dict[str, Any]
        :return:
        :rtype: :class:`AnsibleTest`
        """
        validator = self._test_validator_factory.from_file(self._test_schema)

        if not validator.is_valid(data):
            raise ValueError(
                f"Test data did not conform to schema: '{self._test_schema}'"
            )

        return self._parse_suites(data)

    def _parse_suites(self, data):
        result = []

        for suite in data:
            result += self._parse_suite(suite)

        return result

    def _parse_suite(self, data):
        result = []

        phase = data['phase']

        for play in data['plays']:
            suite = TestSuite(
                name=play['play']['name']
            )

            for task in play['tasks']:
                test = AnsibleTest(
                    phase=phase,
                    name=task['task']['name'],
                    duration=self._get_task_duration(task)
                )

                for host in task['hosts']:
                    test.hosts.append(
                        AnsibleTestHost(
                            name=host,
                            action=task['hosts'][host]['action'],
                            result=self._get_host_result(task, host)
                        )
                    )

                suite.tests.append(test)

            result.append(suite)

        return result

    def _get_host_result(self, task, host):
        if task['hosts'][host].get('skipped', False):
            return AnsibleTestStatus.SKIPPED

        if task['hosts'][host].get('changed', False):
            return AnsibleTestStatus.CHANGED

        if task['hosts'][host].get('failed', False):
            return AnsibleTestStatus.FAILURE

        return AnsibleTestStatus.SUCCESS

    def _get_task_duration(self, task):
        start = dateutil.parser.parse(task['task']['duration']['start'])
        end = dateutil.parser.parse(task['task']['duration']['end'])

        return (end - start).total_seconds()
