# -*- coding: utf-8 -*-
"""
toylang log
"""

from enum import IntEnum


class LogLevel(IntEnum):
    NONE        = 0
    ERROR       = 1
    WARNING     = 2
    INFO        = 3
    DEBUG       = 4
    ALL         = 5


global_log_level = LogLevel.ERROR


def set_log_level(level):
    global global_log_level
    global_log_level = level


def log(level, msg):
    if level <= global_log_level:
        print(msg)


def error(msg):
    log(LogLevel.ERROR, msg)


def warning(msg):
    log(LogLevel.WARNING, msg)


def info(msg):
    log(LogLevel.INFO, msg)


def debug(msg):
    log(LogLevel.DEBUG, msg)


def all(msg):
    log(LogLevel.ALL, msg)
