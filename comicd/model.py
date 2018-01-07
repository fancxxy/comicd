#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from comicd.utils import LazyProperty as Lazy
from comicd.error import ComicdError
from re import compile
from os import makedirs
from os.path import join, exists, abspath
from comicd.interface import interface
from comicd.config import config


class Model(object):
    def __init__(self):
        self.instance = None
        self.repeat = 1

    @classmethod
    def find(cls, url):
        try:
            pattern = compile(r'https?://([^/]+?)/')
            host = pattern.search(url).group(1)
            return interface[host]
        except (AttributeError, KeyError):
            raise ComicdError('comicd does not support this website')


class Comic(Model):
    def __init__(self, url):
        super().__init__()

        self.instance = Model.find(url)
        self.url = self._check(url)

    def init(self):
        if self.title == '' or self.chapters == []:
            return False
        else:
            return True

    @Lazy
    def data(self):
        return self.instance.comic(self.url)

    @Lazy
    def title(self):
        title = ''
        if self.data:
            title = self.instance.title(self.data)
        return title

    @Lazy
    def chapters(self):
        chapters = []
        if self.data:
            chapters = self.instance.chapters(self.data)
        return chapters

    def download_cover(self, path):
        complete, binary = False, None
        if self.data:
            binary = self.instance.cover(self.data)
            abs_path = abspath(path)
            if not exists(abs_path):
                makedirs(abs_path)
            with open(join(abs_path, self.instance.name + '_' + self.title + '.jpg'), 'wb') as image:
                image.write(binary)
            complete = True
        return complete

    @Lazy
    def count(self):
        if self.chapters:
            return len(self.chapters)
        else:
            return 0

    def latest(self):
        return self.__getitem__(self.count - 1)

    def download(self):
        from comicd.crawler import Crawler
        crawler = Crawler()
        crawler.put('Comic', self)
        crawler.crawl()

    def _check(self, raw_url):
        url = self.instance.url(raw_url)
        if not url:
            raise ComicdError('chapter url is incorrect')
        return url

    def __getitem__(self, index):
        if self.chapters:
            return Chapter(self.chapters[index][1])
        else:
            return None

    def __repr__(self):
        return '<Comic object interface=\'{}\' title=\'{}\'>'.format(self.instance.name, self.title)

    __str__ = __repr__


class Chapter(Model):
    def __init__(self, url):
        super().__init__()

        self.instance = Model.find(url)
        self.url = self._check(url)

    def init(self):
        if self.ctitle == '' or self.title == '' or self.images == []:
            return False
        else:
            return True

    @Lazy
    def data(self):
        return self.instance.chapter(self.url)

    @Lazy
    def title(self):
        title = ''
        if self.data:
            title = self.instance.cctitle(self.data)
        return title

    @Lazy
    def ctitle(self):
        ctitle = ''
        if self.data:
            ctitle = self.instance.cptitle(self.data)
        return ctitle

    @Lazy
    def images(self):
        images = []
        if self.data:
            images = self.instance.images(self.data)
        return images

    @Lazy
    def count(self):
        if self.images:
            return len(self.images)
        else:
            return 0

    def download(self):
        from comicd.crawler import Crawler
        crawler = Crawler()
        crawler.put('Chapter', self)
        crawler.crawl(0, 1, config.threads[2])

    def _check(self, raw_url):
        url = self.instance.curl(raw_url)
        if not url:
            raise ComicdError('chapter url is incorrect')
        return url

    def __repr__(self):
        return '<Chapter object interface=\'{}\' title=\'{}\' ctitle=\'{}\'>'.format(self.instance.name, self.title,
                                                                                     self.ctitle)

    __str__ = __repr__


class Image(Model):
    def __init__(self, url, instance, filename, referer, title=None, ctitle=None, page=None):
        super().__init__()
        self.url = url
        self.instance = instance
        self.filename = filename
        self.referer = referer

        self.title = title
        self.ctitle = ctitle
        self.page = page

    def download(self):
        complete = False
        binary = self.instance.image(self.url, self.referer)
        if binary:
            with open(self.filename, 'wb') as image:
                image.write(binary)
            complete = True
        return complete

    def __repr__(self):
        return '<Image object interface=\'{}\' title=\'{}\', ' \
               'ctitle=\'{}\', page=\'{}\'>'.format(self.instance.name, self.title, self.ctitle, self.page)

    __str__ = __repr__


class Folder(object):
    def __init__(self, home, title, ctitle):
        self.title = title
        self.ctitle = ctitle
        self.path = join(home, self._quote(self.title), self._quote(self.ctitle))

    def create(self):
        if not exists(self.path):
            makedirs(self.path)
        return self.path

    @staticmethod
    def _quote(title):
        return title.replace('/', '／')
