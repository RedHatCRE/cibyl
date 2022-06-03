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
import logging

from cibyl.exceptions.source import InvalidArgument
from cibyl.sources.plugins import SourceExtension

LOG = logging.getLogger(__name__)


class ServerSource(SourceExtension):
    """A class representation of a source that must connect to a server
    instance."""

    def check_jobs_for_spec(self, jobs_found, **kwargs):
        """Ensure that only one job was found if using the --spec argument,
        raise a different exception in the cases where no job is found, and
        multiple jobs are found."""
        spec = "spec" in kwargs
        if spec:
            spec_value = kwargs["spec"].value
            jobs_args = kwargs.get("jobs")
            # if user called cibyl just with --spec without value and no --jobs
            # argument, we have not enough information to pull the spec
            spec_missing_input = not bool(spec_value) and (jobs_args is None)
            if len(jobs_found) == 0 or spec_missing_input:
                msg = "No job was found, please pass --spec job-name with an "
                msg += " exact match or --jobs job-name with a valid job name "
                msg += "or pattern."
                raise InvalidArgument(msg)

            if len(jobs_found) > 1:
                msg = "Full Openstack specification can be shown only for "
                msg += " one job, please restrict the query."
                raise InvalidArgument(msg)
