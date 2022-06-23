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


class SourceMethodsStore:
    """Store the source queries that have been performed. This will allow
    us to avoid sending multiple times the same queries if there are multiple
    arguments that are associated with the same function (for example --builds
    and --build-status).
    """
    def __init__(self):
        self.cache = {}

    def _method_information_tuple(self, source_method):
        """Obtain a tuple representation in the format (source_name,
        method_name) from the input source_method.

        :param source_method: Source method that is used
        :type source_method: method
        :returns: The internal representation of the source_method in the cache
        :rtype: tuple(str, str)
        """
        source = source_method.__self__
        method_name = source_method.__name__
        return (source.name, method_name)

    def has_been_called(self, source_method):
        """Check whether a particular source method has already been called
        before.

        :param source_method: Source method that is used
        :type source_method: method
        :returns: Whether the source method has been called before
        :rtype: bool
        """
        return self._method_information_tuple(source_method) in self.cache

    def add_call(self, source_method, success):
        """Add a particular source method to the call cache, with a given
        status.

        :param source_method: Source method that is used
        :type source_method: method
        :param success: Whether the source method call was successful
        :type success: bool
        """
        self.cache[self._method_information_tuple(source_method)] = success

    def get_status(self, source_method):
        """Return the success of a previous call to source_method.

        :param source_method: Source method that is used
        :type source_method: method
        """
        return self.cache[self._method_information_tuple(source_method)]
