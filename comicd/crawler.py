#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from threading import Thread, Lock
from queue import Queue, Empty
from signal import signal, SIGINT
from pickle import dump, load
from os.path import join, exists
from time import sleep
from comicd.model import Model, Comic, Chapter, Image, Folder
from comicd.error import ComicdError
from comicd.config import config
from comicd.log import Log

interrupt = False


class CrawlerThread(Thread):
    def __init__(self, handler, crawler, name):
        super().__init__(name=name)
        self.crawler = crawler
        self.handler = handler

    def run(self):
        while not interrupt:
            try:
                task = self.crawler.get(self.name)
                if self.handler(task):
                    self.crawler.put(self.name, task)
                else:
                    self.crawler.exception(self.name, task)
                self.crawler.finish(self.name)
            except Empty:
                if self.crawler.complete(self.name):
                    break


class Crawler(object):
    def __init__(self):
        self._queue = {'Comic': Queue(), 'Chapter': Queue(), 'Image': Queue()}

        self._lock = Lock()

        self._config = config

        self._log = Log()

        signal(SIGINT, Crawler.sig_handler)

    def initialize(self, urls):
        for u in urls:
            model, url = self._parse(u)
            if model:
                self._queue[model].put(eval('{}(url)'.format(model)))

        self.crawl()

    def crawl(self, comic_thread=None, chapter_thread=None, image_thread=None):

        comic_threads = [CrawlerThread(handler=Comic.init, crawler=self, name='Comic')
                         for _ in range(comic_thread if comic_thread else self._config.threads[0])]

        chapter_threads = [CrawlerThread(handler=Chapter.init, crawler=self, name='Chapter')
                           for _ in range(chapter_thread if chapter_thread else self._config.threads[1])]

        image_threads = [CrawlerThread(handler=Image.download, crawler=self, name='Image')
                         for _ in range(image_thread if image_thread else self._config.threads[2])]

        [t.start() for t in comic_threads]
        sleep(1)
        [t.start() for t in chapter_threads]
        sleep(1)
        [t.start() for t in image_threads]

        [t.join() for t in (*comic_threads, *chapter_threads, *image_threads)]

        if interrupt:
            self.serialize()

    def put(self, name, task):
        if name == 'Comic':
            for chapter in task.chapters:
                try:
                    self._queue['Chapter'].put(Chapter(chapter[1]))
                except ComicdError:
                    self._log.warning('cannot handle url {}'.format(chapter[1]))
        elif name == 'Chapter':
            f = Folder(self._config.home, task.title, task.ctitle)
            self._queue['Image'].put(f)
            for image in task.images:
                try:
                    self._queue['Image'].put(Image(image[1], task.instance,
                                                   join(f.path, image[0]),
                                                   task.url, task.title,
                                                   task.ctitle, image[0]))
                except ComicdError:
                    self._log.warning('cannot handle url {}'.format(image[1]))

    def get(self, name):
        if name == 'Comic' or name == 'Chapter':
            task = self._queue[name].get(timeout=1)
        else:  # name == 'Image'
            with self._lock:
                task = self._queue[name].get(timeout=1)
                while isinstance(task, Folder):
                    task.create()
                    self._log.info(' <' + task.title + '> ' + task.ctitle)
                    task = self._queue[name].get(timeout=1)
        return task

    def finish(self, name):
        self._queue[name].task_done()

    def complete(self, name):
        if name == 'Comic':
            return True
        elif name == 'Chapter':
            return self._queue['Comic'].empty()
        elif name == 'Image':
            return self._queue['Comic'].empty() and self._queue['Chapter'].empty()

    def exception(self, name, task):
        if task.repeat >= self._config.repeat:
            self._log.warning('handle task {} failed'.format(task))
        else:
            task.repeat += 1
            self._queue[name].put(task)

    def _parse(self, raw_url):
        try:
            instance = Model.find(raw_url)
            url = instance.curl(raw_url)
            if url:
                return 'Chapter', url
            url = instance.url(raw_url)
            if url:
                return 'Comic', url
        except ComicdError:
            self._log.warning('cannot handle url {}'.format(raw_url))
            return None, raw_url

    def serialize(self):
        with open(self._config.serialize, 'wb') as f:
            dump((self._queue['Comic'].queue, self._queue['Chapter'].queue, self._queue['Image'].queue), f)

    def deserialize(self):
        if not exists(self._config.serialize):
            self._log.error('no serialize file found')
            return

        with open(self._config.serialize, 'rb') as f:
            q1, q2, q3 = load(f)
            [self._queue['Comic'].put(item) for item in list(q1)]
            [self._queue['Chapter'].put(item) for item in list(q2)]
            [self._queue['Image'].put(item) for item in list(q3)]

        self.crawl()

    @staticmethod
    def sig_handler(signum, frame):
        global interrupt
        interrupt = True
