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
from enum import Enum

from cibyl.models.ci.base.job import Job


class LastBuildEnum(str, Enum):
    lastBuild = "lastBuild"
    # Jenkins meaning of lastCompletedBuild is slightly different from what we
    # have used, lastCompletedBuild will return also builds that failed,
    # lastSuccessfulBuild is what we want
    lastCompletedBuild = "lastSuccessfulBuild"


def has_tests_job(job: Job) -> bool:
    """Check if a job has any tests added.
    :param job: Job to check
    :returns: whether the job has any tests
    """
    for build in job.builds.values():
        if build.tests.value:
            return True
    return False


def has_builds_job(job: Job) -> bool:
    """Check if a job has any builds added.
    :param job: Job to check
    :returns: whether the job has any builds
    """
    return bool(job.builds.value)
