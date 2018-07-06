#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from comicd.interface import Web
from comicd.utils import unpack
from re import compile


class Verydm(Web):
    name = '非常爱漫'
    host = ['www.verydm.com', 'imgn1.magentozh.com:8090']

    _pattern = {
        'comic_url': compile(r'^http://www.verydm.com/manhua/(.*?)$'),
        'chapter_url': compile(r'^http://www.verydm.com/chapter.php\?id=\d+$'),
        'summary': compile(r'<div id="content_wrapper">(.*?)</div>'),

        'title': compile(r'<div class="comic-name">\s+<h1>(.*?)</h1>'),
        'scope': compile(r'(?s)<div class="head">连载列表</div>(.*?)</ul>'),
        'chapters': compile(r'<a href="(.*?)" target=\'_blank\' title="(.*?)">'),
        'cover': compile(r'<img src="(.*?)" class="cover"/>'),
        'ctitle': compile(r'您现在的位置：<a href=".*?">首页</a> &gt; <a href=".*?">(.*?)</a> &gt; <span>(.*?)</span>'),
        # 'function': compile(r'(?<=eval\()(.*?)$'),
        'function': compile(r'(?s)eval\((.*?)\)\s+</script>'),
        'image': compile(r'"(.*?)"')
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
        content, url = data
        try:
            cover_url = self._pattern['cover'].search(content).group(1)
            return self._request.binary(cover_url, headers={'Host': self.host[1], 'Referer': url})
        except AttributeError:
            return None

    def summary(self, data):
        content = data[0]
        try:
            return self._pattern['summary'].search(content).group(1).strip()
        except AttributeError:
            return ''

    def chapters(self, data):
        content = data[0]
        try:
            scope = self._pattern['scope'].search(content).group(1)
            chapters = self._pattern['chapters'].findall(scope)[::-1]
            return [(c[1], 'http://www.verydm.com' + c[0]) for c in chapters]
        except AttributeError:
            return []

    def cctitle(self, data):
        content = data[0]
        try:
            return self._pattern['ctitle'].search(content).group(1)
        except AttributeError:
            return ''

    def cptitle(self, data):
        content = data[0]
        try:
            return self._pattern['ctitle'].search(content).group(2)
        except AttributeError:
            return ''

    def images(self, data):
        images = data[1]
        if images:
            count, result = 1, []
            for i in images:
                result.append(('{:0>3}.jpg'.format(count), i.replace('\\', '')))
                count += 1
            return result
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
