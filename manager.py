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
import zlib

from Util import *
from addr import *
from index import *
from block import *
from entrystore import *
from dump_cache import *

class CacheManager(object):
  def __init__(self, fromDir=None, toDir=None):
    self.fromDir = fromDir
    self.toDir = toDir
    self.indexFile = None;
    self.blockFiles = [None] * 4;   # data_0, data_1, data_2, data_3
    self.separateFiles = {}

    self.entries = []

    if fromDir:
      self.indexFile = Index(pathToIndex=os.path.join(fromDir, "index"))
      self.blockFiles[0] = Block(pathToBlock=os.path.join(fromDir, "data_0"))
      self.blockFiles[1] = Block(pathToBlock=os.path.join(fromDir, "data_1"))
      self.blockFiles[2] = Block(pathToBlock=os.path.join(fromDir, "data_2"))
      self.blockFiles[3] = Block(pathToBlock=os.path.join(fromDir, "data_3"))

      separate_files = [name for name in os.listdir(fromDir) if os.path.isfile(os.path.join(fromDir, name)) and name[0] == 'f']
      for fname in separate_files:
        with open(os.path.join(fromDir, fname), 'rb') as tmp:
          self.separateFiles[fname] = tmp.read()

  def processEntries(self):
    assert(self.indexFile.table)

    for addr in self.indexFile.table:
      entry = EntryStore(self.fetchBytesForEntry(addr), self)
      self.entries.append(entry)

      if entry.next_addr:
        self.indexFile.table.append(CacheAddr(entry.next_addr))

  def outputToFiles(self):
    dumper = CacheDumper(self.toDir)
    dumper.init()

    count = 0
    for entry in self.entries:
      if len(entry.response_header) <= 1:
        continue

      url = entry.key.encode('utf-8')
      ext = getExt(entry.key, entry.headerMap)
      dumper.insert(url, '\n'.join(entry.response_header), isHeader=True)

      if len(entry.data) > 1:
        contentEncoding = entry.headerMap.get('Content-Encoding')
        if not contentEncoding:
          contentEncoding = entry.headerMap.get('content-encoding')
        if contentEncoding:
          try:
            entry.data[1] = zlib.decompress(entry.data[1], 16+zlib.MAX_WBITS)
          except:
            pass

        dumper.insert(url, entry.data[1], ext=ext)


  def fetchBytesForEntry(self, addr):
    block_file = addr.block_file
    block_number = addr.block_number
    num_blocks = addr.contiguous_blocks + 1
    
    entries = self.blockFiles[block_file].getEntry(block_number, num_blocks)
    return b"".join(entries)

  def insertAddrToIndex(self, addr):
    self.indexFile.table.append(CacheAddr(addr))

