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
    self.table = None
    self.data = None

    if pathToIndex:
      with open(pathToIndex, 'rb') as f:
        self.data = f.read()

      self.parse(self.data)
      

  def parse(self, data):
    self.header = IndexHeader(headData=self.data)
    self.table = []

    d = self.data
    l = self.header.table_len
    o = self.header.offset

    #rawTable = [byteToInt(d[o+4*i:o+4*i+4]) for i in range(0, l + 4) if isCacheInitialized(d[o+4*i:o+4*i+4])]
    rawTable = [readNextFourBytesAsInt(d, o+4*i) for i in range(0, l + 4) if isCacheInitialized(d[o+4*i: o+4*i+4])]


    self.table = [CacheAddr(addr) for addr in rawTable]
    print(self.table)

  def getEntry(self, index):
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
    self.magic = readNextFourBytesAsInt(data, offset)
    offset += 4
    self.version = readNextFourBytesAsInt(data, offset)
    offset += 4
    self.num_entries = readNextFourBytesAsInt(data, offset)
    offset += 4
    self.num_bytes = readNextFourBytesAsInt(data, offset)
    offset += 4
    self.last_file = readNextFourBytesAsInt(data, offset)
    offset += 4
    self.this_id = readNextFourBytesAsInt(data, offset)
    offset += 4
    self.stats = readNextFourBytesAsInt(data, offset)
    offset += 4
    self.table_len = readNextFourBytesAsInt(data, offset)
    offset += 4
    self.crash = readNextFourBytesAsInt(data, offset)
    offset += 4
    self.experiment = readNextFourBytesAsInt(data, offset)
    offset += 4
    self.create_time = byteToInt(data[offset:offset+8])
    offset += 8

    # ignore LruData
    self.offset = 368


class LruData(object):
  def __init__(self):
    pass


