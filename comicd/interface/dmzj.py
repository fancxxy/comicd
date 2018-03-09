#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.parse import unquote
from os.path import split
from re import compile
from comicd.utils import unpack
from comicd.interface import Web


class Dmzj(Web):
    name = '动漫之家'
    host = ['manhua.dmzj.com', 'images.dmzj.com']

    _pattern = {
        'title': compile(r'<h1>(.*?)</h1>'),
        'scope': compile(r'(?s)<div class="cartoon_online_border" [^>]*>\s+(.*?)<div class="clearfix"></div>'),
        'chapter': compile(r'<li><a title=".*?" href="(.*?)" +(class="color_red")?>(.*?)</a>'),
        'chapter_principal': compile(r'<li><a title="([^-]+-第\d+话)" href="(.*?)" +(class="color_red")?>'),
        'function': compile(r'(?s)eval\((.*?)\)\s+;'),
        'image': compile(r'"(.*?)"'),
        'comic_title': compile(r'var g_comic_name = "(.*?)";'),
        'chapter_title': compile(r'var g_chapter_name = "(.*?)";'),

        'comic_url': compile(r'^https://manhua.dmzj.com/(\w+)/?$'),
        'chapter_url': compile(r'^https://manhua.dmzj.com/(\w+)/\d+\.shtml'),
        'cover': compile(
            r'<div class="anim_intro_ptext">\s+<a href=".*?"><img alt=".*?" src="(.*?)" id="cover_pic"/></a>')
    }

    def __init__(self):
        super().__init__()

    def comic(self, url):
        return [self._request.content(url, headers={'Host': self.host[0]}), url]

    def chapter(self, url):
        content = self._request.content(url, headers={'Host': self.host[0]})
        return [content, self._unpack_javascript(content)]

    def image(self, url, referer):
        return self._request.binary(url, headers={'Host': self.host[1], 'Referer': referer})

    def title(self, data):
        content = data[0]
        try:
            return self._pattern['title'].search(content).group(1)
        except AttributeError:
            return ''

    def cover(self, data):
        content = data[0]
        url = data[1]
        try:
            cover_url = self._pattern['cover'].search(content).group(1)
            return self._request.binary(cover_url, headers={'Host': self.host[1], 'Referer': url})
        except AttributeError:
            return None

    def chapters(self, data):
        content = data[0]
        try:
            scope = ' '.join(self._pattern['scope'].findall(content))
            chapters = self._pattern['chapter'].findall(scope)
            return [(c[2], 'http://manhua.dmzj.com' + c[0]) for c in chapters]

        except AttributeError:
            return []

    def cctitle(self, data):
        content = data[0]
        try:
            return self._pattern['comic_title'].search(content).group(1)
        except AttributeError:
            return ''

    def cptitle(self, data):
        content = data[0]
        try:
            return self._pattern['chapter_title'].search(content).group(1)
        except AttributeError:
            return ''

    def images(self, data):
        images = data[1]
        if images:
            return [(unquote(split(i)[1]), ('http://images.dmzj.com/' + i).replace('\\', '')) for i in images]
        else:
            return []

    def _unpack_javascript(self, content):
        try:
            javascript = self._pattern['function'].search(content).group(1)
            data = unpack(javascript)
            images = self._pattern['image'].findall(data)
            return images
        except AttributeError:
            return None
