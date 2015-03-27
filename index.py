import sys
import struct
import os
import threading
import json
import time
import re
import urllib
import uuid
import hashlib
import shutil
import logging

from Util import *
from addr import *

# https://chromium.googlesource.com/chromium/src.git/+/master/net/disk_cache/blockfile/disk_format.h


# index file
kIndexTablesize = 0x10000
kIndexMagic = 0xC103CAC3
kCurrentVersion = 0x20000

class Index(object):
    def __init__(self, pathToIndex=None):
        self.header = None
        self.table = []

        if pathToIndex:
            data = None
            with open(pathToIndex, 'rb') as f:
                data = f.read()

            self.header = IndexHeader(headData=data)
            self.parse_body(data)


    def parse_body(self, data):
        d = data
        l = self.header.table_len
        o = self.header.offset

        for i in range(0, l):
            if is_cache_initialized(d[o+4*i:o+4*i+4]):
                self.table.append(CacheAddr(read_next_four_byte_as_int(d, o+4*i)))

    def get_entry(self, index):
        return self.table[i]


class IndexHeader(object):
    def __init__(self, headData=None):
        self.magic = None
        self.version = None
        self.num_entries = None   # Number of entries currently stored
        self.num_bytes = None     # Total size of the stored data
        self.last_file = None     # Last external file created
        self.this_id = None       # Id for all entries being changed (dirty flag)
        self.stats = None         # Storage for usage data
        self.table_len = None     # Actual size of the table (0 == kIndexTablesize)
        self.crash = None         # Signals a previous crash
        self.experiment = None    # Id of an ongoing test
        self.create_time = None   # Creation time for this set of files
        self.lru = None           # Eviction control data = None

        self.offset = 0

        if headData:
            self.parse(headData)

    def parse(self, data):
        offset = 0
        self.magic = read_next_four_byte_as_int(data, offset)
        offset += 4
        self.version = read_next_four_byte_as_int(data, offset)
        offset += 4
        self.num_entries = read_next_four_byte_as_int(data, offset)
        offset += 4
        self.num_bytes = read_next_four_byte_as_int(data, offset)
        offset += 4
        self.last_file = read_next_four_byte_as_int(data, offset)
        offset += 4
        self.this_id = read_next_four_byte_as_int(data, offset)
        offset += 4
        self.stats = read_next_four_byte_as_int(data, offset)
        offset += 4
        self.table_len = read_next_four_byte_as_int(data, offset)
        offset += 4
        self.crash = read_next_four_byte_as_int(data, offset)
        offset += 4
        self.experiment = read_next_four_byte_as_int(data, offset)
        offset += 4
        self.create_time = byte_to_int(data[offset:offset+8])
        offset += 8

        # ignore LruData
        self.offset = 368


class LruData(object):
    def __init__(self):
        pass
