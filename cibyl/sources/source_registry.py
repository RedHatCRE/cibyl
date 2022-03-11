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


# pylint: disable=too-few-public-methods
class SourceRegistry:
    """Relates driver names to Source classes.

    The format of the mapping is "driver name": ("source module", "source
    class").
    """
    sources = {
            "jenkins": ("cibyl.sources.jenkins", "Jenkins"),
            "jenkins_job_builder": ("cibyl.sources.jenkins_job_builder",
                                    "JenkinsJobBuilder"),
            "zuul": ("cibyl.sources.zuul", ""),
            "elasticsearch": ("cibyl.sources.elasticsearch", "")
            }
