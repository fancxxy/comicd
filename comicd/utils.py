#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from re import search, sub


def unpack(code):
    """
    unpack javascript function, copy from youtube-dl
    """
    PACKED_CODES_RE = r"}\('(.+)',(\d+),(\d+),'([^']+)'\.split\('\|'\)"

    def basen(num, n, table=None):
        FULL_TABLE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if not table:
            table = FULL_TABLE[:n]

        if n > len(table):
            raise ValueError('base %d exceeds table length %d' % (n, len(table)))

        if num == 0:
            return table[0]

        ret = ''
        while num:
            ret = table[num % n] + ret
            num = num // n
        return ret

    mobj = search(PACKED_CODES_RE, code)
    obfucasted_code, base, count, symbols = mobj.groups()
    base = int(base)
    count = int(count)
    symbols = symbols.split('|')
    symbol_table = {}

    while count:
        count -= 1
        base_n_count = basen(count, base)
        symbol_table[base_n_count] = symbols[count] or base_n_count

    return sub(r'\b(\w+)\b', lambda mobj: symbol_table[mobj.group(0)], obfucasted_code)


class LazyProperty(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        val = self.func(instance)
        setattr(instance, self.func.__name__, val)
        return val
