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
import importlib.util
import inspect
from types import ModuleType
from typing import Callable, List, Optional

from cibyl.utils.files import get_file_name_from_path


def load_module(path: str) -> ModuleType:
    """Loads a Python module given its location.

    :param path: Absolute path to the module to be loaded.
    :return: The loaded module.
    """
    spec = importlib.util.spec_from_file_location(
        get_file_name_from_path(path), path
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


def get_classes_in(
        __module: ModuleType,
        predicate: Optional[Callable] = None,
        return_name: bool = False) -> List[type]:
    """Gets all class symbols stored within a Python module.

    :param __module: The module to get the classes from.
    :param predicate: A callable to pass to inspect.getmembers to filter the
    symbols found
    :param return_name: Whether to return the name of the classes found, as
    inpect.getmembers does
    :return: List of all classes stored in the module.
    """
    if predicate is None:
        predicate = inspect.isclass
    if return_name:
        return inspect.getmembers(__module, predicate)
    else:
        return [cls for _, cls in inspect.getmembers(__module, predicate)]
