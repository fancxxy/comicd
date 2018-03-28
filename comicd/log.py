#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from sys import stderr


class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class Log(Singleton):
    def __init__(self):
        if not hasattr(self, 'logger'):
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
