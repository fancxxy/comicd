#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from comicd.model import Comic


class TestComic(unittest.TestCase):
    info = [
        {
            'url': 'http://manhua.dmzj.com/yiquanchaoren/',
            'title': '一拳超人',
            'ctitle': '第124话',
            'pages': 57
        },
        {
            'url': 'https://manhua.163.com/source/4458002705630123103',
            'title': '天才麻将少女',
            'ctitle': '第1话 邂逅',
            'pages': 32
        },
        {
            'url': 'https://manhua.163.com/source/5015375858980120764',
            'title': '银魂',
            'ctitle': '1',
            'pages': 58
        },
        {
            'url': 'http://ac.qq.com/Comic/comicInfo/id/505430',
            'title': '航海王',
            'ctitle': '第1话 ROMANCE DAWN',
            'pages': 57
        },
        {
            'url': 'http://ac.qq.com/Comic/comicInfo/id/505432',
            'title': '火影忍者',
            'ctitle': '第1话 旋涡鸣人',
            'pages': 61
        }
    ]

    def test_comic(self):
        for info in self.info:
            with self.subTest(info=info):
                comic = Comic(info['url'])
                self.assertTrue(comic.title, info['title'])

                chapter = comic[1]
                self.assertNotEqual(chapter, None)
                self.assertTrue(chapter.title, info['title'])
                self.assertTrue(chapter.ctitle, info['ctitle'])
                self.assertTrue(chapter.count, info['pages'])
