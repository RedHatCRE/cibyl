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
from abc import abstractmethod
from operator import itemgetter
from typing import Any, Dict, Optional

import requests

from cibyl.cli.argument import Argument
from cibyl.exceptions.source import NoSupportedSourcesFound, NoValidSources
from cibyl.utils.attrdict import AttrDict

LOG = logging.getLogger(__name__)


def safe_request_generic(request, custom_error):
    """Decorator that wraps any errors coming out of a call around a
    custom_error class.

    :param request: The unsafe call to watch errors on.
    :param custom_error: Error type used to wrap any error coming out of
        the request.
    :return: The input call decorated to raise the desired error type.
    """

    def request_handler(*args, **kwargs):
        """Calls the unsafe function and wraps any errors coming out of it
        around a custom_error class.

        :param args: Arguments with which the function is called.
        :return: Output of the called function.
        """
        try:
            return request(*args, **kwargs)
        except requests.exceptions.SSLError as ex:
            raise custom_error(
                "Please set certificates in order to connect to the system \
or add 'cert: False' to the configuration"
            ) from ex
        except requests.exceptions.ConnectionError as ex:
            raise custom_error(
                "Could not connect to target host, please ensure connection "
                "details are correct."
            ) from ex
        except requests.exceptions.HTTPError as ex:
            extra_info = "."
            if ex.response.status_code:
                extra_info = " - Unauthorized. Check login details"
            raise custom_error(
                 f"Got response {ex.response.status_code} from target \
host{extra_info}"
            ) from ex
        except Exception as ex:
            raise custom_error('Failure on request to target host.'
                               f' {str(ex)}') from ex

    return request_handler


class Source(AttrDict):
    """Represents a data provider within a system."""

    def __init__(self,
                 name: str = Optional[str],
                 driver: str = Optional[str],
                 **kwargs: Any):
        kwargs.setdefault('enabled', True)
        kwargs.setdefault('_setup', False)
        kwargs.setdefault('_down', False)
        kwargs.setdefault('priority', 0)

        super().__init__(name=name, driver=driver, **kwargs)

    def is_setup(self) -> bool:
        """Return wether the source has been setup."""
        return self._setup

    def ensure_source_setup(self) -> None:
        """Ensure that setup is called for the source. If setup was previously
        called, do nothing."""
        if not self.is_setup():
            self._setup = True
            self.setup()

    def is_down(self) -> bool:
        """Return wether the source has been teardown."""
        return self._down

    def ensure_teardown(self) -> None:
        """Ensure that teardown is called for the source. If teardown was
        previously called, do nothing."""
        if self.is_setup() and not self.is_down():
            self._down = True
            self.teardown()

    @abstractmethod
    def setup(self) -> None:
        """Setup everything required for the source to become operational."""
        pass

    @abstractmethod
    def teardown(self) -> None:
        """Release any resources allocated during setup."""
        pass

    def disable(self) -> None:
        """Set source as disabled."""
        self.enabled = False


def is_source_valid(source: Source, desired_attr: str):
    """Checks if a source can be considered valid to perform a query.

    For a source to be considered valid it must:
        * Be enabled.
        * Have the attribute passed as input.

    :param source: The source to check.
    :type source: :class:`Source`
    :param desired_attr: An attribute that is useful for performing a
        query and that is desired for the source to have.
    :type desired_attr: str
    :return: Whether the source is valid or not.
    :rtype: bool
    """
    if not source.enabled:
        return False

    if not hasattr(source, desired_attr):
        return False

    return True


def get_source_speed_score(source, func_name: str, args: Dict[str, Argument]):
    """Get the speed index for a source's method according to user input.

    :param source: Source to evaluate
    :type source: :class:`.Source`
    :param func_name: Source's method to evaluate
    :type func_name: str
    :param args: User input arguments
    :type args: dict
    """
    source_method = getattr(source, func_name)
    speed = source_method.speed_index.get('base', 0)
    for arg in args:
        speed += source_method.speed_index.get(arg, 0)
    return speed


def get_source_method(system_name: str, sources: list, func_name: str,
                      args: Dict[str, Argument]):
    """Returns a list of sources' methods that provided the functionality
    requested by the user sorted by the speed index.

    :param system_name: The name of system
    :type system_name: str
    :param sources: List of Source instances
    :type sources: list[Source]
    :param func_name: The name of the function to invoke
    :type func_name: str
    :param args: User input arguments
    :type args: dict
    :raises: NoSupportedSourcesFound if no sources with the function name are
    found
    :returns: List of pairs with source method and its speed index sorted by
    the speed index
    :rtype: tuple
    """

    valid_sources = []
    for source in sources:
        if is_source_valid(source, func_name):
            source_speed_score = get_source_speed_score(source,
                                                        func_name, args)
            source_method = getattr(source, func_name)
            valid_sources.append((source_method, source_speed_score))

    if not valid_sources:
        raise NoSupportedSourcesFound(system_name, func_name)

    return sorted(valid_sources, key=itemgetter(1), reverse=True)


def speed_index(speed):
    """Add a speed index to sources methods to select the best one according to
    user input.
    """
    def decorator(func):
        setattr(func, 'speed_index', speed)
        return func
    return decorator


def source_information_from_method(source_method):
    """Obtain source information from a method of a source object.

    :param source_method: Source method that is used
    :type source_method: method
    :returns: string with source information identifying the object that the
    method belongs to
    :rtype: str
    """
    source = source_method.__self__
    info_str = f"source: '{source.name}' of type: '{source.driver}'"
    if LOG.getEffectiveLevel() <= logging.DEBUG:
        info_str += f" using method {source_method.__name__}"
    return info_str


def select_source_method(system, method, **kwargs):
    """Select the apropiate source considering the user input.

    :param system: system to select sources from
    :type system: :class:`.System`
    :param argument: argument that is considered for the query
    :type argument: :class:`.Argument`

    :returns: List of pairs with source method and its speed index sorted
    by the speed index value
    :rtype: tuple
    """
    sources_user = kwargs.get("sources")
    system_sources = system.sources
    if sources_user:
        system_sources = [source for source in system.sources if
                          source.name in sources_user.value]
    if not system_sources:
        raise NoValidSources(system,
                             [source.name for source in system.sources])
    return get_source_method(system.name.value, system_sources,
                             method, args=kwargs)


def get_source_instance_from_method(source_method):
    """Obtain the source object from a method that belongs to said object.

    :param source_method: Source method that is used
    :type source_method: method
    :returns: source instance the input method belongs to
    :rtype: :class:`.Source`
    """
    return source_method.__self__
