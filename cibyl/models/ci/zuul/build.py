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
from overrides import overrides

from cibyl.models.ci.base.build import Build as BaseBuild


class Build(BaseBuild):
    """Representation of a build on a zuul environment.

    @DynamicAttrs: Contains attributes added on runtime.
    """

    class Info:
        """Data class containing all information that defines a build.
        """

        def __init__(self, project, pipeline, uuid, result, duration):
            """Constructor.
            
            :param project: The project the build belongs to.
            :type project: str 
            :param pipeline: Pipeline that triggered the build.
            :type pipeline: str
            :param uuid: ID of the build.
            :type uuid: str
            :param result: Result of the build.
            :type result: str
            :param duration: Time, in seconds, that the build took to complete.
            :type duration: int
            """
            self.project = project
            self.pipeline = pipeline
            self.uuid = uuid
            self.result = result
            self.duration = duration

    API = {
        **BaseBuild.API,
        'project': {
            'attr_type': str,
            'arguments': []
        },
        'pipeline': {
            'attr_type': str,
            'arguments': []
        }
    }
    """Defines the contents of the model."""

    def __init__(self, info, tests=None):
        """Constructor.

        :param info: Data that defines this build.
        :type info: :class:`Build.Info`
        :param tests: Tests under this build.
        :type tests: list[:class:`cibyl.models.ci.base.test.Test`] or None
        """
        super().__init__(
            build_id=info.uuid,
            status=info.result,
            duration=info.duration,
            tests=tests,
            project=info.project,
            pipeline=info.pipeline
        )

    @overrides
    def __eq__(self, other):
        if not isinstance(other, Build):
            return False

        if self is other:
            return True

        return \
            self.build_id == other.build_id and \
            self.status == other.status and \
            self.duration == other.duration and \
            self.tests == other.tests and \
            self.project == other.project and \
            self.pipeline == other.pipeline
