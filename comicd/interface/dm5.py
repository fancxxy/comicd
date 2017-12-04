#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from re import compile, sub
from comicd.interface import Web
from comicd.utils import unpack
from urllib.parse import urlparse


class Dm5(Web):
    name = '动漫屋'
    host = ['www.dm5.com', ]

    _pattern = {
        'title': compile(r'<div class="inbt"><h1 class="new_h2">(.*?)</h1>'),
        'scope': compile(r'<ul class="nr7">.*?</ul>(.*?)<div class="ff"></div>'),
        'chapters': compile(r'<a class="tg" href="(.*?)" title="(.*?)">'),

        'comic_url': compile(r'^http://www.dm5.com/manhua-[^/]+/?$'),
        'chapter_url': compile(r'^http://www.dm5.com/\w+/?$'),

        'dm5_ctitle': compile(r'''(?x)<span\ class="center">(<a\ href=".*?">.*?</a>\ >\ ){2}
                                           <a\ href=".*?">([^\ ]+)\ 漫画</a>\ >\ <h1\ class="active">(.*?)</h1></span>'''),
        'dm5_curl': compile(r'var DM5_CURL = "(.*?)"'),
        'dm5_cid': compile(r'var DM5_CID=(.*?);'),
        'dm5_count': compile(r'var DM5_IMAGE_COUNT=(.*?);'),
        'dm5_key_script': compile(r'''(?x)<input\ type="hidden"\ id="dm5_key"\ value=""\ />\s+
                                                <script\ type="text/javascript">\ (.*?)\n</script>'''),

        'js_function': compile(r'eval\((.*)\)'),
        'dm5_key': compile(r';var [^=]+=(.*?);'),

        'url_pre': compile(r'var pix="(.*?)";'),
        'url_in': compile(r'"/(.*?)"'),
        'url_post': compile(r'(\?cid=\d+&key=\w+)'),

        'filename': compile(r'http://(.*?/)+(.*?)\?cid=')
    }

    def __init__(self):
        super().__init__()

    def comic(self, url):
        return [self._request.content(url, headers={'Host': self.host[0], 'Referer': 'http://www.dm5.com/'})]

    def chapter(self, url):
        return [self._request.content(url, headers={'Host': self.host[0]})]

    def image(self, url, referer):
        try:
            content = self._request.content(url, headers={'Host': self.host[0], 'Referer': referer})
            data = unpack(content)
            url_pre = self._pattern['url_pre'].search(data).group(1)
            url_in = self._pattern['url_in'].search(data).group(1)
            url_post = self._pattern['url_post'].search(data).group(1)

            host = urlparse(url_pre).netloc

            url = url_pre + '/' + url_in + url_post
            # filename = self._pattern['filename'].search(url).group(2)

            return self._request.binary(url, headers={'Host': host, 'Referer': referer})
        except AttributeError:
            return b''

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
            chapters = self._pattern['chapters'].findall(scope)
            return [(c[1], 'http://www.dm5.com' + c[0]) for c in chapters]
        except AttributeError:
            return []

    def cctitle(self, data):
        content = data[0]
        try:
            return self._pattern['dm5_ctitle'].search(content).group(2)
        except AttributeError:
            return ''

    def cptitle(self, data):
        content = data[0]
        try:
            return self._pattern['dm5_ctitle'].search(content).group(3)
        except AttributeError:
            return ''

    def images(self, data):
        content = data[0]
        try:
            curl = 'http://www.dm5.com' + self._pattern['dm5_curl'].search(content).group(1)
            cid = self._pattern['dm5_cid'].search(content).group(1)
            count = self._pattern['dm5_count'].search(content).group(1)
            key = self._dm5_key(content)
            url = '%schapterfun.ashx?cid=%s&page={}&key=%slanguage=%d&gtk=%d' % (curl, cid, key, 1, 6)
            return [('{:03}.jpg'.format(page), url.format(page)) for page in range(1, int(count) + 1)]  # xhr
        except AttributeError:
            return []

    def _dm5_key(self, content):
        result = self._pattern['dm5_key_script'].search(content)
        if result:
            script = result.group(1)
            data = unpack(script)
            return sub(r'[\\\'+]', '', self._pattern['dm5_key'].search(data).group(1))
        else:
            return ''
