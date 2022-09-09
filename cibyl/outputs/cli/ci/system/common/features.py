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
from cibyl.cli.query import QueryType


def is_features_query(query: QueryType) -> bool:
    """Checks the query involves a feature command. This might be a features
    call with or without --jobs flag.

    :param query: The query to check.
    :return: True if the query involves a features subcommand, False if not.
    """
    return QueryType.FEATURES in query


def is_pure_features_query(query: QueryType) -> bool:
    """Checks the query involves a feature command without calling for --jobs.

    :param query: The query to check.
    :return: True if the query involves a features subcommand without a --jobs
        flag, False if not.
    """
    return is_features_query(query) and QueryType.JOBS not in query
