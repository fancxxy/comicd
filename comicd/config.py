#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import expanduser, join
from comicd.utils import Singleton


class Config(Singleton):
    def __init__(self, home='~/Comics', comic=1, chapter=1, image=5, repeat=3, mode='crawler', proxy_api=None):
        self._home = expanduser(home)

        self.log = join(self._home, '.comicd.log')

        self.serialize = join(self._home, '.comicd.dat')

        self._threads = [comic, chapter, image]

        self.repeat = repeat

        self.mode = mode

        self.proxy = None

    @property
    def home(self):
        return self._home

    @home.setter
    def home(self, value):
        self._home = expanduser(value)

    @property
    def threads(self):
        return self._threads

    @threads.setter
    def threads(self, value):
        if not isinstance(value, list) or len(value) != 3:
            value = [1, 1, 5]
        self._threads = value

    def __call__(self, home='~/Comics', comic=1, chapter=1, image=5, repeat=3, mode='crawler', proxy_api=None):
        self.__init__(home, comic, chapter, image, repeat, mode, proxy_api)
        return self

    def __repr__(self):
        return '<Config object home=\'{}\' threads={{comic:{}, chapter:{}, image:{}}} repeat={} mode={}> proxy_api={}'.format(
            self._home, self.threads[0], self.threads[1], self.threads[2], self.repeat, self.mode, self.proxy)

    __str__ = __repr__


config = Config()
