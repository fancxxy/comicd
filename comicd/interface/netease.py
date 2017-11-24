#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from json import loads, JSONDecodeError
from re import compile, sub
from comicd.interface import Web


class Netease(Web):
    name = '网易漫画'
    host = ['manhua.163.com', 'nos.netease.com']

    _pattern = {
        'comic_url': compile(r'^https://manhua.163.com/source/(\d+)/?$'),
        'chapter_url': compile(r'^https://manhua.163.com/reader/\d+/\d+'),
        'title': compile(r'<h1 class="f-toe sr-detail__heading">(.*?)</h1>'),
        'pg_config': compile(r'(?s)window.PG_CONFIG = (.*?);'),
        'pg_config_images': compile(r'(?s)window.PG_CONFIG.images = (.*?);'),
        'image_url': compile(r'''(?x)title:\ "([^"]+)",\nwidth[^\n]+\nheight[^\n]+\nimageType[^\n]+\npath[^\n]+\n
                         indexId[^\n]+\nverifyStatus[^\n]+\nurl:\ window.IS_SUPPORT_WEBP\ \?\ "[^"]+"\ :\ "([^"]+)"'''),
        'image_suffix': compile(r'(.*?)(?<=%3D)')
    }

    def __init__(self):
        super().__init__()

    def comic(self, url):
        try:
            xhr_url = 'https://manhua.163.com/book/catalog/' + self._pattern['comic_url'].search(url).group(1) + '.json'
            data = loads(self._request.content(xhr_url, headers={'Host': self.host[0], 'Referer': url}))
            return [self._request.content(url, headers={'Host': self.host[0]}), data]
        except (AttributeError, JSONDecodeError):
            return ['', '']

    def chapter(self, url):
        content = self._request.content(url, headers={'Host': self.host[0]})
        return [content, self._parse_json('pg_config', content), self._parse_json('pg_config_images', content)]

    def image(self, url, referer):
        return self._request.binary(url, headers={'Host': self.host[1], 'Referer': referer})

    def title(self, data):
        content = data[0]
        try:
            return self._pattern['title'].search(content).group(1)
        except AttributeError:
            return ''

    def chapters(self, data):
        try:
            return [(c['title'], 'https://manhua.163.com/reader/' + c['bookId'] + '/' + c['sectionId']) for c in
                    data[1]['catalog']['sections'][0]['sections']]
        except KeyError:
            return []

    def cctitle(self, data):
        try:
            return data[1]['book']['title']
        except KeyError:
            return ''

    def cptitle(self, data):
        try:
            return data[1]['section']['fullTitle']
        except KeyError:
            return ''

    def images(self, data):
        try:
            return [(record['title'] + ('.jpg' if record['title'].find('.') == -1 else ''),
                     self._pattern['image_suffix'].match(record['url']).group(1)) for record in data[2]]
        except AttributeError:
            return ''

    def _parse_json(self, pattern, content):
        try:
            string = self._pattern[pattern].search(content).group(1)
            string = sub(r'(\w+): [\w.]+ \? (.*?) : (.*?),', r'\1: \3,', string)
            string = sub(r'(\w+): ', r'"\1": ', string)

            return loads(string)
        except (AttributeError, JSONDecodeError):
            return {}
