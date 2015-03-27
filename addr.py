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

"""
  bit masks for cache address
"""
CACHE_ADDR_INIT_MASK = 0x80000000
CACHE_ADDR_INIT_OFFSET = 31

CACHE_ADDR_FILETYPE_MASK = 0x70000000
CACHE_ADDR_FILETYPE_OFFSET = 28

CACHE_ADDR_FILENUMBER_MASK = 0x0FFFFFFF
CACHE_ADDR_FILENUMBER_OFFSET = 0

CACHE_ADDR_RESERVED_MASK = 0x0C0000000
CACHE_ADDR_RESERVED_OFFSET = 26

CACHE_ADDR_CONTIGUOUSBLOCK_MASK = 0x03000000
CACHE_ADDR_CONTIGUOUSBLOCK_OFFSET = 24

CACHE_ADDR_BLOCKFILE_MASK = 0x00FF0000
CACHE_ADDR_BLOCKFILE_OFFSET = 16

CACHE_ADDR_BLOCKNUMBER_MASK = 0x0000FFFF
CACHE_ADDR_BLOCKNUMBER_OFFSET = 0


class CacheAddr(object):
    def __init__(self, addr=0):
        self.addr = addr
        self.init = (addr & CACHE_ADDR_INIT_MASK) >> CACHE_ADDR_INIT_OFFSET
        self.file_type = (addr & CACHE_ADDR_FILETYPE_MASK) >> CACHE_ADDR_FILETYPE_OFFSET

        # separate file
        self.file_number = (addr & CACHE_ADDR_FILENUMBER_MASK) >> CACHE_ADDR_FILENUMBER_OFFSET

        # block file
        self.reserved = (addr & CACHE_ADDR_RESERVED_MASK) >> CACHE_ADDR_RESERVED_OFFSET
        self.contiguous_blocks = (addr & CACHE_ADDR_CONTIGUOUSBLOCK_MASK) >> CACHE_ADDR_CONTIGUOUSBLOCK_OFFSET
        self.block_file = (addr & CACHE_ADDR_BLOCKFILE_MASK) >> CACHE_ADDR_BLOCKFILE_OFFSET
        self.block_number = (addr & CACHE_ADDR_BLOCKNUMBER_MASK) >> CACHE_ADDR_BLOCKNUMBER_OFFSET

    def __repr__(self):
        output = """_______________________________\n
         {0}\n_______________________________\n""".format(hex(self.addr))
        if self.file_type == 0:
            output += """Init: {0}\nFile Type: {1}\nFile Number: {2}\n""".format(
                self.init,
                self.filetype_to_string(),
                self.file_number)
        else:
            output += """Init: {0}\nFile Type: {1}\nContiguous Blocks: {2}\nBlock File: {3}\nBlock Number: {4}\n""".format(
                self.init,
                self.filetype_to_string(),
                self.contiguous_blocks,
                self.block_file,
                self.block_number)
        return output


    def filetype_to_string(self):
        if self.file_type < 0 or self.file_type > 4:
            return "Unknown file type"

        return {
            0: "separate file",
            1: "ranking block-file",
            2: "256 bytes block-file",
            3: "1k bytes block-file",
            4: "4k bytes block-file"
        }[self.file_type]

