#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import listdir
from os.path import dirname, splitext
from importlib import import_module
from comicd.request import Request


class Interface(object):
    def __init__(self):
        self._interface = {}

        path = dirname(__file__)
        for file in listdir(path):
            name, extension = splitext(file)
            if name == '__init__' or extension != '.py':
                continue
            mod = import_module('comicd.interface.' + name)
            cls = getattr(mod, name.capitalize())
            host = getattr(cls, 'host')
            self._interface[host[0]] = cls()

    def __getitem__(self, key):
        return self._interface[key]

    @property
    def lists(self):
        return {cls.name for cls in self._interface.values()}

    @lists.setter
    def lists(self, value):
        raise AttributeError('lists is not a writable attribute')


class Web(object):
    _pattern = {}

    def __init__(self):
        self._request = Request()

    def url(self, url):
        try:
            return self._pattern['comic_url'].match(url).group()
        except AttributeError:
            return ''

    def curl(self, url):
        try:
            return self._pattern['chapter_url'].match(url).group()
        except AttributeError:
            return ''


interface = Interface()
