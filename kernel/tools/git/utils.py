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

from tripleo.utils.urls import URL, is_git


def get_repository_fullname(url: URL) -> str:
    """Gets the fullname of a repository from its URL.

    URL formats supported are:
        - HTTP/HTTPS
        - SSH

    Examples
    --------
    >>> cibyl = URL('https://github.com/rhos-infra/cibyl.git')
    ... get_repository_fullname(cibyl)
    'rhos-infra/cibyl'

    :param url: The URL to get the data from.
    :return: The fullname in the format: '{owner}/{name}'
    :raises ValueError: If the URL does not point to a git repository.
    """
    if not is_git(url):
        msg = f"URL must point to a git repository: '{url}'."
        raise ValueError(msg)

    path = urlparse(url).path
    path = path[1:]  # Remove leading '/'
    path = path[:-4]  # Remove trailing '.git'

    return path
