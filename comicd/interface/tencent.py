#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from base64 import b64decode
from json import loads
from re import compile
from comicd.interface import Web


class Tencent(Web):
    name = '腾讯漫画'
    host = ['ac.qq.com', 'ac.tc.qq.com']

    _pattern = {
        'comic_url': compile(r'^http://ac.qq.com/Comic/[Cc]omicInfo/id/(.+)/?$'),
        'chapter_url': compile(r'^http://ac.qq.com/ComicView/index/id/(\d+)/cid/\d+/?$'),

        'title': compile(r'<h2 class="works-intro-title ui-left"><strong>(.*?)</strong></h2>'),
        'scope': compile(r'(?s)<div class="works-chapter-list-wr ui-left">(.*?)</ol>'),
        'chapter': compile(r'<a target="_blank" title=[\'\"][^：]+：(.*?)[\'\"] href=[\'\"](.*?)[\'\"]>'),
        'javascript': compile(r'var\s+DATA\s+=\s+\'(.*?)\'')
    }

    def __init__(self):
        super().__init__()

    def comic(self, url):
        return [self._request.content(url, headers={'Host': self.host[0]})]

    def chapter(self, url):
        content = self._request.content(url, headers={'Host': self.host[0]})
        return [content, self._parse_javascript(content)]

    def image(self, url, referer):
        return self._request.binary(url, headers={'Host': self.host[1], 'Referer': referer})

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

    def title(self, data):
        content = data[0]
        try:
            return self._pattern['title'].search(content).group(1)
        except AttributeError:
            return ''

    def chapters(self, data):
        content = data[0]
        try:
            scope = self._pattern['scope'].search(content).group(1)
            chapters = self._pattern['chapter'].findall(scope)
            return [(c[0], 'http://ac.qq.com' + c[1]) for c in chapters]
        except AttributeError:
            return []

    def cctitle(self, data):
        try:
            return data[1]['comic']['title']
        except KeyError:
            return ''

    def cptitle(self, data):
        try:
            return data[1]['chapter']['cTitle']
        except KeyError:
            return ''

    def images(self, data):
        try:
            return [(p['pid'] + '.jpg', p['url']) for p in data[1]['picture']]
        except KeyError:
            return []

    def _parse_javascript(self, content):
        try:
            data = self._pattern['javascript'].search(content).group(1)
        except AttributeError:
            return {}
        return loads(b64decode(data[1:]))
