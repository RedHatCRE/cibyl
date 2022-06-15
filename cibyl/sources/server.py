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

from cibyl.exceptions.source import MissingArgument
from cibyl.sources.source import Source

LOG = logging.getLogger(__name__)


class ServerSource(Source):
    """A class representation of a source that must connect to a server
    instance."""

    # pylint: disable=too-many-arguments
    def check_builds_for_test(self, **kwargs):
        """Ensure that some build information is passed when requesting
        tests."""
        if not any(arg in kwargs for arg in ('builds', 'last_build')):
            raise MissingArgument('Please specify some builds (--builds) \
to get the tests from. Or use (--last-build) to get the tests from the last \
one')
