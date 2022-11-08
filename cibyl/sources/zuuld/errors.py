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


class ZuulDError(Exception):
    """Generic error occurring on the Zuul.d API.
    """


class InvalidURL(ZuulDError):
    """A URL does not conform to its expected structure.
    """


class IllegibleData(ZuulDError):
    """Some data read by the API does not conform to the structure expected
    by it.
    """
