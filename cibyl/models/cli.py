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


class QueryType(Enum):
    NONE = 0
    TENANTS = 1
    JOBS = 2
    BUILDS = 3


def get_query_type(**kwargs):
    result = QueryType.NONE

    if 'tenants' in kwargs:
        result = QueryType.TENANTS

    if 'jobs' in kwargs:
        result = QueryType.JOBS

    if 'builds' in kwargs:
        result = QueryType.BUILDS

    return result
