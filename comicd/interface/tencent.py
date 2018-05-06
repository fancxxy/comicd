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
        'summary': compile(r'(?s)<p class="works-intro-short ui-text-gray9">\s+(.*?)</p>'),

        'title': compile(r'<h2 class="works-intro-title ui-left"><strong>(.*?)</strong></h2>'),
        'scope': compile(r'(?s)<div class="works-chapter-list-wr ui-left">(.*?)</ol>'),
        'chapters': compile(r'<a target="_blank" title=[\'\"][^：]+：(.*?)[\'\"] href=[\'\"](.*?)[\'\"]>'),
        'javascript': compile(r'var\s+DATA\s+=\s+\'(.*?)\''),

        'cover': compile(r'<img src="(.*?)" alt=".*?" height="280" width="210"/>'),
        'update': compile(r'''(?x)<span\ class="ui-font-fb">最新话：</span><a\ class="works-ft-new"\ href="(.*?)">\[(.*?)\]
            (</a><span\ class="ui-pl10\ ui-text-gray6">(.*?)</span>)?''')
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

    def title(self, data):
        content = data[0]
        try:
            return self._pattern['title'].search(content).group(1)
        except AttributeError:
            return ''

    def cover(self, data):
        content = data[0]
        try:
            cover_url = self._pattern['cover'].search(content).group(1)
            return self._request.binary(cover_url)
        except AttributeError:
            return None

    def summary(self, data):
        content = data[0]
        try:
            return self._pattern['summary'].search(content).group(1)
        except AttributeError:
            return ''

    def update(self, data):
        content = data[0]
        try:
            # abandon second value
            newest_url, newest_title, _, newest_date = self._pattern['update'].findall(content)[0]
            return 'http://ac.qq.com' + newest_url, newest_title, newest_date.replace('.', '-')
        except AttributeError:
            return '', '', ''

    def chapters(self, data):
        content = data[0]
        try:
            scope = self._pattern['scope'].search(content).group(1)
            chapters = self._pattern['chapters'].findall(scope)
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
            # return [(p['pid'] + '.jpg', p['url']) for p in data[1]['picture']]
            count, result = 1, []
            for p in data[1]['picture']:
                result.append(('{:0>3}.jpg'.format(count), p['url']))
                count += 1
            return result
        except KeyError:
            return []

    def _parse_javascript(self, content):
        try:
            data = self._pattern['javascript'].search(content).group(1)
        except AttributeError:
            return {}
        return loads(b64decode(data[1:]))
