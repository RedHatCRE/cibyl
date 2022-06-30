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
from urllib.parse import urlparse

from tripleo.utils.types import URL


def is_git(url: URL) -> bool:
    """
    :param url: The URL to test.
    :return: True if the URL points to a git repository, False if not.
    """
    return url.endswith('.git')


def is_github(url: URL) -> bool:
    """
    :param url: The URL to test.
    :return: True if the URL has GitHub as its host, False if not.
    """
    result = urlparse(url)

    return 'github' in result.hostname
