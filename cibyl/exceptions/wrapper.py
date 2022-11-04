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
import functools
from typing import Type

from cibyl.exceptions import CibylException


def wrap_exception(wrapper: Type[CibylException], message: str = ''):
    """Decorator that catches any errors coming out of the wrapped function
    and wraps them around with one from the given type.

    Wrapping error will still reference the original error as its cause.
    This can be accessed through the '__cause__' attribute of the error.

    Example:
    >>> @wrap_exception(CibylException)
    ... def unsafe_io():
    ...     raise IOError

    :param wrapper: Type of error that will wrap any coming from the function.
    :param message: Additional text displayed by the wrapping error.
    :return: The decorator function.
    """

    def decorator(func):
        def wrapped(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as ex:
                raise wrapper(message) from ex

        return functools.wraps(func)(wrapped)

    return decorator
