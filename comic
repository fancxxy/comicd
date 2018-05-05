#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from comicd.config import config
from os.path import exists
from os import makedirs


def comicd():
    if not exists(config.home):
        makedirs(config.home)

    parser = ArgumentParser(description='Comic Download Tool')
    parser.add_argument('-u', '--url', nargs='+', dest='urls', help='urls of comics')
    parser.add_argument('-r', '--resume', action='store_true', default=False, dest='resume',
                        help='resume last crawl task')
    parser.add_argument('-f', '--file', action='store', dest='file', help='crawl from file')
    args = parser.parse_args()

    urls = []

    from comicd.crawler import Crawler
    crawler = Crawler()

    if args.resume:
        crawler.deserialize()
        exit(0)

    if args.urls:
        urls = args.urls
    elif args.file:
        with open(args.file, 'r') as f:
            urls = [u for u in f.readlines()]

    crawler.initialize(urls)


if __name__ == '__main__':
    comicd()

