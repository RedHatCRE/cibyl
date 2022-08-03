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
from cibyl.sources.zuul.apis import ZuulBuildAPI as Build
from cibyl.sources.zuul.utils.artifacts.manifest import ManifestFile
from cibyl.utils.urls import URL


def get_url_to_build_file(build: Build, file: ManifestFile) -> URL:
    """Generates the URL to a file published by the build's manifest. No checks
    are performed to ensure that the file belongs to the build or that the
    URL points to an existing resource.

    Examples:
    >>> get_url_to_build_file(Build(...), ManifestFile('/var/log/file.log'))
    'http://localhost:8080/log/server/var/log/file.log'

    :param build: The build to use as reference.
    :param file: Relative path to a file using the manifest's root as the
        starting point.
    :return: URL where the file can be downloaded from.
    """
    # Take away starting '/' of the file path to avoid repetition
    return URL(f'{build.log_url}{file[1:]}')
