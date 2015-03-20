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

#from Util import byteToInt
from Util import *

# https://chromium.googlesource.com/chromium/src.git/+/master/net/disk_cache/blockfile/disk_format.h

# index file
kIndexTablesize = 0x10000
kIndexMagic = 0xC103CAC3
kCurrentVersion = 0x20000

# block file
kBlockMagic = 0xC104CAC3;
kBlockHeaderSize = 8192;
kMaxBlocks = (kBlockHeaderSize - 80) * 8
kNumExtraBlocks = 1024

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

class CacheManager(object):
  def __init__(self, pathToDir=None):
    self.pathToDir = pathToDir
    self.indexFile = None;
    self.blockFiles = [None] * 4;   # data_0, data_1, data_2, data_3
    self.separateFiles = []

    if pathToDir:
      self.indexFile = Index(pathToIndex=os.path.join(pathToDir, "index"))
      #self.blockFiles[1] = Bl



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

    rawTable = [byteToInt(d[o+4*i:o+4*i+4]) for i in range(0, l + 4) if isCacheInitialized(d[o+4*i:o+4*i+4])]
    #rawTable = [byteToInt(d[o+4*i:o+4*i+4]) for i in range(0, l + 4)]
    self.table = [CacheAddr(addr) for addr in rawTable]

    #for e in rawTable:
      #print(hex(e))
    #print(self.table)
    #print(self.table[0].__repr__())
    #print(len(self.table))

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
    self.offset = 0
    self.magic = byteToInt(data[self.offset:self.offset+4])
    self.offset += 4
    self.version = byteToInt(data[self.offset:self.offset+4])
    self.offset += 4
    self.num_entries = byteToInt(data[self.offset:self.offset+4])
    self.offset += 4
    self.num_bytes = byteToInt(data[self.offset:self.offset+4])
    self.offset += 4
    self.last_file = byteToInt(data[self.offset:self.offset+4])
    self.offset += 4
    self.this_id = byteToInt(data[self.offset:self.offset+4])
    self.offset += 4
    self.stats = byteToInt(data[self.offset:self.offset+4])
    self.offset += 4
    self.table_len = byteToInt(data[self.offset:self.offset+4])
    self.offset += 4
    self.crash = byteToInt(data[self.offset:self.offset+4])
    self.offset += 4
    self.experiment = byteToInt(data[self.offset:self.offset+4])
    self.offset += 4
    self.create_time = byteToInt(data[self.offset:self.offset+8])
    self.offset += 8

    # ignore LruData
    self.offset = 368


class LruData(object):
  def __init__(self):
    pass



class CacheAddr(object):
  def __init__(self, addr=0):
    self.addr = addr
    self.init = (addr & CACHE_ADDR_INIT_MASK) >> CACHE_ADDR_INIT_OFFSET
    self.fileType = (addr & CACHE_ADDR_FILETYPE_MASK) >> CACHE_ADDR_FILETYPE_OFFSET

    # separate file
    self.FileNumber = (addr & CACHE_ADDR_FILENUMBER_MASK) >> CACHE_ADDR_FILENUMBER_OFFSET

    # block file
    self.reserved = (addr & CACHE_ADDR_RESERVED_MASK) >> CACHE_ADDR_RESERVED_OFFSET
    self.contiguousBlocks = (addr & CACHE_ADDR_CONTIGUOUSBLOCK_MASK) >> CACHE_ADDR_CONTIGUOUSBLOCK_OFFSET
    self.blockFile = (addr & CACHE_ADDR_BLOCKFILE_MASK) >> CACHE_ADDR_BLOCKFILE_OFFSET
    self.blockNumber = (addr & CACHE_ADDR_BLOCKNUMBER_MASK) >> CACHE_ADDR_BLOCKNUMBER_OFFSET

  def __repr__(self):
    output = """_______________________________\n
         {0}\n_______________________________\n""".format(hex(self.addr))
    if self.fileType == 0:
      output += """Init: {0}\nFile Type: {1}\nFile Number: {2}\n""".format(
          self.init,
          self.fileTypeToString(),
          self.FileNumber)
    else:
      output += """Init: {0}\nFile Type: {1}\nContiguous Blocks: {2}\nBlock File: {3}\nBlock Number: {4}\n""".format(
          self.init,
          self.fileTypeToString(),
          self.contiguousBlocks,
          self.blockFile,
          self.blockNumber)
    return output


  def fileTypeToString(self):
    return {
      0: "separate file",
      1: "ranking block-file",
      2: "256 bytes block-file",
      3: "1k bytes block-file",
      4: "4k bytes block-file"
    }[self.fileType]


class Block(object):
  def __init__(self):
    self.magic;
    self.version;
    self.this_file;
    self.next_file;
    self.entry_size;
    self.num_entries;
    self.max_entries;
    self.empty = [0] * 4
    self.hints = [0] * 4
    self.user = [0] * 5
    self.allocation_map = [0] * (kMaxBlocks / 32)

  def parseHeader(self, data):
    pass
    


class EntryStore(object):
  def __init__(self):
    self.hash = None               # Full hash of the key.
    self.next = None               # Next entry with the same hash or bucket.
    self.rankings_node = None      # Rankings node for this entry.
    self.reuse_count = None        # How often is this entry used.
    self.refetch_count = None      # How often is this fetched from the net.
    self.state = None              # Current state.
    self.creation_time = None
    self.key_len = None
    self.long_key = None           # Optional address of a long key.
    self.data_size = [None] * 4    # We can store up to 4 data streams for each
    self.data_addr = [None] * 4    # entry.
    self.flags = None              # Any combination of EntryFlags.
    self.pad[4] = [None] * 4
    self.self_hash = None          # The hash of EntryStore up to this point.
    self.key = [None] * (256 - 24 * 4)  # null terminated
