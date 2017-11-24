#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import urllib.error
from re import compile
from time import strftime, time, localtime
from gzip import decompress


class Request(object):
    default = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.5',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0'
    }

    def request(self, url, data=None, headers=None):
        if headers:
            headers = {**self.default, **headers}
        else:
            headers = self.default
        url = urllib.parse.quote(url, safe='%/:?=&[]')
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req) as res:
                if res.getheader('Content-Encoding') == 'gzip':
                    res = decompress(res.read())
                else:
                    res = res.read()
                return res
        except Exception as e:
            return None

    def content(self, url, data=None, headers=None):
        response = self.request(url, data, headers)
        if response:
            return response.decode('utf-8', 'ignore')
        else:
            return ''

    def page(self, url, file=None, data=None, headers=None):
        response = self.request(url, data, headers).decode('utf-8', 'ignore')
        if not response:
            return False

        if not file:
            pattern = compile(r'(?<=<title>).*?(?=</title>)')
            result = pattern.search(response)
            if result:
                file = result.group(0)
            else:
                file = 'comic_' + strftime('%Y%m%d_%H%M%S', localtime(time()))
        with open(file + '.html', 'wb') as f:
            f.write(response.encode('utf-8'))

        return True

    def binary(self, url, data=None, headers=None):
        response = self.request(url, data=data, headers=headers)
        if response:
            return response
        else:
            return b''
