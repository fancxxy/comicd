#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import shutil

import os

from comicd.model import Comic


class TestComic(unittest.TestCase):
    info = [
        {
            'url': 'http://manhua.dmzj.com/yiquanchaoren/',
            'title': '一拳超人',
            'ctitle': '特别篇',
            'pages': 31,
        },
        {
            'url': 'https://manhua.163.com/source/4458002705630123103',
            'title': '天才麻将少女',
            'ctitle': '第1话 邂逅',
            'pages': 33,
        },
        {
            'url': 'https://manhua.163.com/source/5015375858980120764',
            'title': '银魂',
            'ctitle': '1',
            'pages': 59,
        },
        {
            'url': 'http://ac.qq.com/Comic/comicInfo/id/505430',
            'title': '航海王',
            'ctitle': '第1话 ROMANCE DAWN 冒险的序幕',
            'pages': 57,
        },
        {
            'url': 'http://ac.qq.com/Comic/comicInfo/id/505432',
            'title': '火影忍者',
            'ctitle': '第1话 旋涡鸣人',
            'pages': 61,
        },
        {
            'url': 'http://www.dm5.com/manhua-guanlangaoshou/',
            'title': '灌篮高手',
            'ctitle': '灌篮高手第31卷',
            'pages': 93,
        }
    ]

    def test_comic(self):
        for info in self.info:
            with self.subTest(info=info):
                comic = Comic(info['url'])
                self.assertEqual(comic.title, info['title'])
                self.assertTrue(comic.download_cover('./cover'), True)

                chapter = comic[0]
                self.assertNotEqual(chapter, None)
                self.assertEqual(chapter.title, info['title'])
                self.assertEqual(chapter.ctitle, info['ctitle'])
                self.assertEqual(chapter.count, info['pages'])

    def tearDown(self):
        shutil.rmtree(os.path.abspath('./cover'))
