#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from comicd.interface import Interface


class TestInterface(unittest.TestCase):
    hosts = {
        'ac.qq.com': '腾讯漫画',
        'manhua.163.com': '网易漫画',
        'manhua.dmzj.com': '动漫之家',
        'www.dm5.com': '动漫屋'
    }

    def test_interface(self):
        interface = Interface()
        for host, name in self.hosts.items():
            with self.subTest(host=host, name=name):
                self.assertEqual(interface[host].name, name)
