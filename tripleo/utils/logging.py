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
from enum import Enum
from logging import FileHandler, Logger, StreamHandler
from typing import Any, TextIO

import colorlog

from tripleo.utils.fs import File

GENERIC_LOG_FORMAT = '{}%(levelname)-8s %(name)-20s %(message)s'
"""Base format for logging messages."""

STREAM_LOG_FORMAT = colorlog.ColoredFormatter(
    fmt='\r' + GENERIC_LOG_FORMAT.format('%(log_color)s'),
    log_colors={
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red,bg_white'
    }
)
"""Message format used when logging into an IO stream."""

FILE_LOG_FORMAT = logging.Formatter(fmt=GENERIC_LOG_FORMAT.format(''))
"""Message format used when logging into a file."""


class LogOutput(Enum):
    """Defines the options that the logger can output into.
    """
    ToStream = 0
    """Log into an IO stream, like stdout for example."""
    ToFile = 1
    """Log into a file."""


def enable_logging(level: int, output: LogOutput, **kwargs: Any) -> None:
    """Enables logging on this library.

    The library hard uses the standard 'logging' module for this feature.

    Each call to this function will add a new handler to the logger at the
    'tripleo' root folder. Be free to call this function as many times
    as desired to make the logger output into multiple targets.

    :param level: Minimum logging level to output. This should be want of
        the options defined by the standard library, like: logging.INFO.
    :param output: Target where the logger will write into.
    :param kwargs: Additional arguments for each of the output options.
    :key stream: Only used for stream output. The IO stream where the log
        will write to. Type: TextIO. Required.
    :key file: Only used for file output. Path to an existing file that the
        log will write to. Type: str. Required.
    :raises ValueError: If some arguments are missing or are not valid.
    :raises IOError: If the file cannot be opened or written into.
    """
    logger = logging.getLogger('tripleo')
    logger.setLevel(level)

    if output == LogOutput.ToStream:
        if 'stream' not in kwargs:
            msg = "Log output 'ToStream' required key 'stream'."
            raise ValueError(msg)

        stream = kwargs['stream']

        _add_new_stream_handler(logger, stream)
        return

    if output == LogOutput.ToFile:
        if 'file' not in kwargs:
            msg = "Log output 'ToFile' requires key 'file'."
            raise ValueError(msg)

        file = File(kwargs['file'])
        file.check_exists()

        _add_new_file_handler(logger, file)
        return


def _add_new_stream_handler(
    logger: Logger,
    stream: TextIO
) -> None:
    stream_handler = StreamHandler(stream)
    stream_handler.setFormatter(STREAM_LOG_FORMAT)
    stream_handler.setLevel(logger.level)

    logger.addHandler(stream_handler)


def _add_new_file_handler(
    logger: Logger,
    file: File
) -> None:
    file_handler = FileHandler(file, mode='w')
    file_handler.setFormatter(FILE_LOG_FORMAT)
    file_handler.setLevel(logger.level)

    logger.addHandler(file_handler)
