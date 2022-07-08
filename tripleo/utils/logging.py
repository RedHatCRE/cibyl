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
import sys
from enum import Enum
from logging import FileHandler, Logger, StreamHandler
from typing import Any

import colorlog

from tripleo.utils.fs import File

GENERIC_LOG_FORMAT = '{}%(levelname)-8s %(name)-20s %(message)s'

STDOUT_LOG_FORMAT = colorlog.ColoredFormatter(
    fmt='\r' + GENERIC_LOG_FORMAT.format('%(log_color)s'),
    log_colors={
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red,bg_white'
    }
)

FILE_LOG_FORMAT = logging.Formatter(fmt=GENERIC_LOG_FORMAT.format(''))


class LogOutput(Enum):
    StdOut = 0
    ToFile = 1


def enable_logging(level: int, *output: LogOutput, **kwargs: Any) -> None:
    logger = logging.getLogger('tripleo')
    logger.setLevel(level)

    for option in output:
        if option == LogOutput.StdOut:
            _configure_logger_for_std_out(logger)
            continue

        if option == LogOutput.ToFile:
            if 'file' not in kwargs:
                msg = "Log output 'ToFile' requires key 'file'."
                raise ValueError(msg)

            file = File(kwargs['file'])
            file.check_exists()

            _configure_logger_for_file_out(logger, file)
            continue


def _configure_logger_for_std_out(logger: Logger) -> None:
    stream_handler = StreamHandler(sys.stdout)
    stream_handler.setFormatter(STDOUT_LOG_FORMAT)
    stream_handler.setLevel(logger.getEffectiveLevel())

    logger.addHandler(stream_handler)


def _configure_logger_for_file_out(logger: Logger, file: File) -> None:
    file_handler = FileHandler(file, mode='w')
    file_handler.setFormatter(FILE_LOG_FORMAT)
    file_handler.setLevel(logger.getEffectiveLevel())

    logger.addHandler(file_handler)
