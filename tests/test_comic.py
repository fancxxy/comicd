#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import shutil
import json
import os

from comicd import Comic, Chapter


class TestComic(unittest.TestCase):

    def setUp(self):
        with open('comic.json', 'r', encoding='utf-8') as f:
            self.comics = json.load(f)

    def test_comic(self):
        for comic_info in self.comics:
            comic_instance = Comic(comic_info['comic_url'])
            self.url(comic_info, comic_instance)
            self.title(comic_info, comic_instance)
            self.summary(comic_info, comic_instance)
            self.chapter(comic_info, comic_instance)
            self.cover(comic_instance)

            chapter_instance = Chapter(comic_info['chapter_url'])
            self.ctitle(comic_info, chapter_instance)
            self.iurl(comic_info, chapter_instance)
            # self.download_chapter(chapter_instance)

    def url(self, comic_info, comic_instance):
        self.assertEqual(comic_info['comic_url'], comic_instance.url)

    def title(self, comic_info, comic_instance):
        self.assertEqual(comic_info['comic_title'], comic_instance.title)

    def summary(self, comic_info, comic_instance):
        self.assertEqual(comic_info['comic_summary'], comic_instance.summary)

    def chapter(self, comic_info, comic_instance):
        chapter_number = int(comic_info['chapter_number'])
        self.assertEqual(comic_info['chapter_title'], comic_instance.chapters[chapter_number][0])
        self.assertEqual(comic_info['chapter_url'], comic_instance.chapters[chapter_number][1])

    def cover(self, comic_instance):
        self.assertTrue(comic_instance.download_cover('./cover'), True)

    def ctitle(self, comic_info, chapter_instance):
        self.assertEqual(comic_info['comic_title'], chapter_instance.title)
        self.assertEqual(comic_info['chapter_title'], chapter_instance.ctitle)

    def iurl(self, comic_info, chapter_instance):
        image_number = int(comic_info['image_number'])
        self.assertEqual(comic_info['image_filename'], chapter_instance.images[image_number][0])
        self.assertEqual(comic_info['image_url'], chapter_instance.images[image_number][1])

    # def download_chapter(self, chapter_instance):
    #     chapter_instance.download()

    def tearDown(self):
        shutil.rmtree(os.path.abspath('./cover'))
