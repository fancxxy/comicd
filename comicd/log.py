#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from sys import stderr


class Log(object):
    def __init__(self):
        self.logger = logging.getLogger('comicd')

        handler = logging.StreamHandler(stream=stderr)

        fmt = '%(message)s'
        formatter = logging.Formatter(fmt, datefmt=None)

        handler.setFormatter(formatter)

        self.logger.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)

        self.logger.addHandler(handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)
