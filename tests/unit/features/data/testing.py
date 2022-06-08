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

from cibyl.cli.argument import Argument
from cibyl.features import FeatureTemplate


class Feature1(FeatureTemplate):
    """Feature for testing1"""

    def __init__(self):
        super().__init__("Feature1")

    def get_method_to_query(self):
        return "get_jobs"

    def get_template_args(self):
        jobs = Argument("jobs", arg_type=str,
                        description="jobs",
                        func="get_jobs",
                        value=["pep8"])

        return {"jobs": jobs}


class Feature2(FeatureTemplate):
    """Feature for testing2"""
    def __init__(self):
        super().__init__("Feature2")

    def get_method_to_query(self):
        return "get_jobs"

    def get_template_args(self):
        jobs = Argument("jobs", arg_type=str,
                        description="jobs",
                        func="get_jobs",
                        value=["pep8"])

        return {"jobs": jobs}


class Feature3(FeatureTemplate):
    def __init__(self):
        super().__init__("Feature3")

    def get_method_to_query(self):
        return "get_jobs"

    def get_template_args(self):
        jobs = Argument("jobs", arg_type=str,
                        description="jobs",
                        func="get_jobs",
                        value=["pep8"])

        return {"jobs": jobs}
