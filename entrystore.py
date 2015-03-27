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
import datetime
import zlib

from Util import *
from addr import *

try:
    import cPickle as pickle
except:
    import pickle

class EntryStore(object):
    def __init__(self, data=None, manager=None):
        self.key_hash = None                # Full hash of the key.
        self.next_addr = None               # Next entry with the same hash or bucket.
        self.rankings_node = None           # Rankings node for this entry.
        self.reuse_count = None             # How often is this entry used.
        self.refetch_count = None           # How often is this fetched from the net.
        self.state = None                   # Current state.
        self.creation_time = None
        self.key_len = None
        self.long_key = None                # Optional address of a long key.
        self.data_size = [None] * 4         # We can store up to 4 data streams for each
        self.data_addr = [None] * 4         # entry.
        self.flags = None                   # Any combination of EntryFlags.
        self.pad = [None] * 4
        self.self_hash = None               # The hash of EntryStore up to this point.
        self.key = None

        self.manager = manager
        self.data = []

        self.response_header = None
        self.payload = None

        if data:
            self.parse(data)

    def parse(self, data):
        offset = 0

        self.key_hash = read_next_four_byte_as_int(data, offset)
        offset += 4

        self.next_addr = read_next_four_byte_as_int(data, offset)
        offset += 4

        self.rankings_node = read_next_four_byte_as_int(data, offset)
        offset += 4

        self.reuse_count = read_next_four_byte_as_int(data, offset)
        offset += 4

        self.refetch_count = read_next_four_byte_as_int(data, offset)
        offset += 4

        self.state = read_next_four_byte_as_int(data, offset)
        offset += 4

        self.creation_time = byte_to_int(read_next_x_bytes(data, offset, 8))
        offset += 8

        self.key_len = read_next_four_byte_as_int(data, offset)
        offset += 4

        self.long_key = read_next_four_byte_as_int(data, offset)
        offset += 4

        for i in range(0, len(self.data_size)):
            self.data_size[i] = read_next_four_byte_as_int(data, offset)
            offset += 4

        for i in range(0, len(self.data_addr)):
            self.data_addr[i] = read_next_four_byte_as_int(data, offset)
            offset += 4

        self.flags = read_next_four_byte_as_int(data, offset)
        offset += 4

        for i in range(0, len(self.pad)):
            self.pad[i] = read_next_four_byte_as_int(data, offset)
            offset += 4

        self.self_hash = read_next_four_byte_as_int(data, offset)
        offset += 4

        if self.long_key == 0:
            self.key = read_next_x_bytes(data, offset, self.key_len).decode('utf-8')
        else:
            self.handle_longkey()

        offset += max(256 - 4 * 24, self.key_len)

        if self.key != None and len(self.key) > 0:
            self.load_data()

    def load_data(self):
        for address, size in zip(self.data_addr, self.data_size):

            if address == 0:
                continue

            cacheAddr = CacheAddr(address)

            if cacheAddr.file_type >= 2:
                blockFile = self.manager.blockFiles[cacheAddr.block_file]
                block_number = cacheAddr.block_number
                contiguous_blocks = cacheAddr.contiguous_blocks

                self.data.append(blockFile.read_blocks(block_number, contiguous_blocks + 1)[0:size])
            elif cacheAddr.file_type == 0:
                self.data.append(self.manager.separateFiles["f_"+"{0:06x}".format(cacheAddr.file_number)][0:size])
            else:
                pass

        self.payload = self.data[1] if len(self.data) > 1 else None
        if len(self.data) > 0:
            self.response_header, self.headerMap = parse_http_headers(self.data[0])

    def handle_longkey(self):
        assert(self.long_key != 0)

        addr = CacheAddr(self.long_key)
        keyData = self.manager.fetch_bytes(addr)[0:self.key_len]
        self.key = keyData.decode('utf-8')

