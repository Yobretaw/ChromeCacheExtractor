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

# block file
kBlockMagic = 0xC104CAC3;
kBlockHeaderSize = 8192;
kMaxBlocks = (kBlockHeaderSize - 80) * 8
kNumExtraBlocks = 1024


class Block(object):
    def __init__(self, pathToBlock=None):
        self.magic= None
        self.version= None
        self.this_file= None
        self.next_file= None
        self.entry_size= None
        self.num_entries= None
        self.max_entries= None
        self.empty = [0] * 4
        self.hints = [0] * 4
        self.updating = None
        self.user = [0] * 5
        self.allocation_map = [0] * int(kMaxBlocks >> 5)

        self.offset_block_start = 0
        self.blocks = [None] * (len(self.allocation_map) << 5)

        if pathToBlock:
            self.data = None
            with open(pathToBlock, "rb") as f:
                self.data = f.read()

            offset = self.parse_header()
            self.parse_bitmap(startFromOffset=offset)

    def parse_header(self):
        data = self.data
        offset = 0
        self.magic = read_next_four_byte_as_int(data, offset)
        offset += 4

        self.version = read_next_four_byte_as_int(data, offset)
        offset += 4

        self.this_file = read_next_two_bytes_as_int(data, offset)
        offset += 2

        self.next_file = read_next_two_bytes_as_int(data, offset)
        offset += 2

        self.entry_size = read_next_four_byte_as_int(data, offset)
        offset += 4

        self.num_entries = read_next_four_byte_as_int(data, offset)
        offset += 4

        self.max_entries = read_next_four_byte_as_int(data, offset)
        offset += 4

        for i in range(0, len(self.empty)):
            self.empty[i] = read_next_four_byte_as_int(data, offset)
            offset += 4

        for i in range(0, len(self.hints)):
            self.hints[i] = read_next_four_byte_as_int(data, offset)
            offset += 4

        self.updating = read_next_four_byte_as_int(data, offset)
        offset += 4

        for i in range(0, len(self.user)):
            self.user[i] = read_next_four_byte_as_int(data, offset)
            offset += 4

        for i in range(0, len(self.allocation_map)):
            self.allocation_map[i] = read_next_four_byte_as_int(data, offset)
            offset += 4

        self.offset_block_start = offset
        return offset

    def parse_bitmap(self, startFromOffset=0):
        blockIdx = 0
        offset = startFromOffset
        for i in range(0, len(self.allocation_map)):
            for j in range(0, 32):
                if (self.allocation_map[i] & (1 << j)) != 0:
                    self.blocks[blockIdx] = self.data[offset:offset + self.entry_size]
                blockIdx += 1
                offset += self.entry_size

    def get_entry(self, idx, count=1):
        return self.blocks[idx:idx+count]

    def read_blocks(self, blockIdx, count):
        return read_next_x_bytes(self.data, self.offset_block_start + self.entry_size * blockIdx, self.entry_size * count)
