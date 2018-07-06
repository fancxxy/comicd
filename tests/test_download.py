#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import json
from comicd import Comic, Chapter, Config


class TestDownload(unittest.TestCase):
    def setUp(self):
        with open('comic.json', 'r', encoding='utf-8') as f:
            self.comics = json.load(f)
        # config = Config()
        # config.proxy = 'http://127.0.0.1:5010/get/'

    # def test_download_chapter(self):
    #     for comic_info in self.comics:
    #         chapter_instance = Chapter(comic_info['chapter_url'])
    #         chapter_instance.download()

    def test_download_comic(self):
        for comic_info in self.comics:
            comic_instance = Comic(comic_info['comic_url'])
            comic_instance.download()
