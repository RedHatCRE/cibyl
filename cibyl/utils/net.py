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
import os
from typing import Optional

import requests

LOG = logging.getLogger(__name__)


class DownloadError(Exception):
    """Represents an error during the download of a file.
    """


def download_file(url: str, dest: str) -> None:
    """Downloads a file from a remote host into the local filesystem.

    Supported protocols are:
        * HTTP
        * HTTPS

    Examples
    --------
    >>> download_file(
            'http://localhost/file.txt', '/home/user/my-file.txt'
        )
    >>> download_file(
            'https://user@pass:localhost/file.txt, '/home/user/my-file.txt'
        )

    :param url: The URL where the file is at.
    :type url: str
    :param dest: Path where the file is going to be downloaded at. Must
        contain name of the file.
    :type dest: str
    :raise DownloadError: If the download failed.
    """
    LOG.debug('Creating path to: %s', dest)

    os.makedirs(os.path.dirname(dest), exist_ok=True)

    LOG.info("Downloading file from: '%s'", url)

    with requests.get(url, stream=True) as request:
        if not request.ok:
            raise DownloadError(
                f'Download failed with: {request.status_code}\n'
                f'{request.text}'
            )

        LOG.debug('Saving to: %s', dest)

        with open(dest, 'wb') as file:
            for chunk in request.iter_content(chunk_size=8 * 1024):
                file.write(chunk)


def download_into_memory(url: str,
                         session: Optional[requests.Session] = None
                         ) -> str:
    """Downloads the contents of a URL into memory, leaving the filesystem
    untouched.

    Supported protocols are:
        * HTTP
        * HTTPS

    ..  doctest::
        >>> download_into_memory('http://localhost/file.txt')

    :param url: URL to download.
    :param session: Session used to perform request. This function will not
        close the session, that task is up to the caller.
    :return: Contents of the page.
    :raise DownloadError: If the download failed.
    """
    LOG.info("Downloading file from: '%s'", url)

    request = session.get(url) if session else requests.get(url)

    if not request.ok:
        raise DownloadError(
            f'Download failed with: {request.status_code}\n'
            f'{request.text}'
        )

    return request.content.decode()
