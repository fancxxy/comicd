#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from re import compile
from comicd.interface import Web
from comicd.utils import unpack
from urllib.parse import urlparse


class Dm5(Web):
    name = '动漫屋'
    host = ['www.dm5.com', ]

    _pattern = {
        'comic_url': compile(r'^http://www.dm5.com/manhua-[^/]+/?$'),
        'chapter_url': compile(r'^http://www.dm5.com/\w+/?$'),

        'comic_details': compile(r'(?s)<div class="banner_detail_form">(.*?)(?=</section>)'),
        'chapter_lists': compile(r'<div id="chapterlistload">(.*?)</div>'),

        'title': compile(r'<div class="info">\s+<p class="title">(.*)<span class="right">'),
        'cover': compile(r'<div class="cover">\s+<img src="(.*?)">'),
        'summary': compile(r'<p class="content" style=".*?">(.*?)<a href="###;" class="fold_open">\[\+展开\]</a><span style="display:none">(.*?)<a href="###;" class="fold_close">\[-折叠\]</a></span></p>|(?s)<p class="content" style=".*?">(.*?)</p>'),
        'scope': compile(r'(?s)<ul class="view-win-list detail-list-select" id="detail-list-select-1">(.*?)<ul class="view-win-list detail-list-select"'),
        'chapters': compile(r'<a href="(.*?)" title=".*?" target="_blank" >(.*?)\s+<span>'),

        'cctitle': compile(r'<span class="right-arrow"><a href=".*?" title=".*?">(.*?)</a></span'),
        'cptitle': compile(r'<span class="active right-arrow">(.*?)</span>'),

        'dm5_cid': compile(r'var DM5_CID=(\d+);'),
        'dm5_mid': compile(r'var DM5_MID=(\d+);'),
        'dm5_count': compile(r'var DM5_IMAGE_COUNT=(\d+);'),
        'dm5_sign': compile(r'var DM5_VIEWSIGN="(.*?)";'),
        'dm5_dt': compile(r'var DM5_VIEWSIGN_DT="(.*?)";'),

        'url_pre': compile(r'var pix="(.*?)";'),
        'url_in': compile(r'"/(.*?)"'),
        'url_post': compile(r'(\?cid=\d+&key=\w+)'),
    }

    def __init__(self):
        super().__init__()

    def comic(self, url):
        try:
            data = self._request.content(url, headers={'Host': self.host[0], 'Referer': 'http://www.dm5.com/'})
            comic_details = self._pattern['comic_details'].search(data).group(1)
            chapter_lists = self._pattern['chapter_lists'].search(data).group(1)
            return [comic_details, chapter_lists]
        except AttributeError:
            return ['', '']

    def chapter(self, url):
        return [self._request.content(url, headers={'Host': self.host[0]})]

    def image(self, url, referer):
        try:
            content = self._request.content(url, headers={'Host': self.host[0], 'Referer': referer, 'X-Requested-With': 'XMLHttpRequest'})
            data = unpack(content)
            url_pre = self._pattern['url_pre'].search(data).group(1)
            url_in = self._pattern['url_in'].search(data).group(1)
            url_post = self._pattern['url_post'].search(data).group(1)
            host = urlparse(url_pre).netloc
            url = url_pre + '/' + url_in + url_post
            return self._request.binary(url, headers={'Host': host, 'Referer': referer})
        except AttributeError:
            return b''

    def title(self, data):
        content = data[0]
        try:
            return self._pattern['title'].search(content).group(1).strip(' ')
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
            summary = self._pattern['summary'].findall(content)
            return ''.join(summary[0])
        except AttributeError:
            return ''

    def chapters(self, data):
        content = data[1]
        try:
            scope = self._pattern['scope'].search(content).group(1)
            chapters = self._pattern['chapters'].findall(scope)
            return [(c[1], 'http://www.dm5.com' + c[0]) for c in chapters][::-1]
        except AttributeError:
            return []

    def cctitle(self, data):
        content = data[0]
        try:
            return self._pattern['cctitle'].search(content).group(1).strip(' ')
        except AttributeError:
            return ''

    def cptitle(self, data):
        content = data[0]
        try:
            return self._pattern['cptitle'].search(content).group(1).strip(' ')
        except AttributeError:
            return ''

    def images(self, data):
        content = data[0]
        try:
            dm5_cid = self._pattern['dm5_cid'].search(content).group(1)
            dm5_mid = self._pattern['dm5_mid'].search(content).group(1)
            dm5_count = self._pattern['dm5_count'].search(content).group(1)
            dm5_sign = self._pattern['dm5_sign'].search(content).group(1)
            dm5_dt = self._pattern['dm5_dt'].search(content).group(1).replace(' ', '+')
            url = 'http://www.dm5.com/m%s/chapterfun.ashx?cid=%s&page={}&key=&language=1&gtk=6&_cid=%s&_mid=%s&_dt=%s&_sign=%s' % (dm5_cid, dm5_cid, dm5_cid, dm5_mid, dm5_dt, dm5_sign)
            return [('{:03}.jpg'.format(page), url.format(page)) for page in range(1, int(dm5_count) + 1)]  # xhr
        except AttributeError:
            return []
