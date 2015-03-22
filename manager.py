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
from index import *
from block import *
from entrystore import *

class CacheManager(object):
  def __init__(self, pathToDir=None):
    self.pathToDir = pathToDir
    self.indexFile = None;
    self.blockFiles = [None] * 4;   # data_0, data_1, data_2, data_3
    self.separateFiles = {}

    self.entries = []

    if pathToDir:
      self.indexFile = Index(pathToIndex=os.path.join(pathToDir, "index"))
      self.blockFiles[0] = Block(pathToBlock=os.path.join(pathToDir, "data_0"))
      self.blockFiles[1] = Block(pathToBlock=os.path.join(pathToDir, "data_1"))
      self.blockFiles[2] = Block(pathToBlock=os.path.join(pathToDir, "data_2"))
      self.blockFiles[3] = Block(pathToBlock=os.path.join(pathToDir, "data_3"))

      separate_files = [name for name in os.listdir(pathToDir) if os.path.isfile(os.path.join(pathToDir, name)) and name[0] == 'f']
      for fname in separate_files:
        with open(os.path.join(pathToDir, fname), 'rb') as tmp:
          print(fname)
          self.separateFiles[fname] = tmp.read()

  def processIndex(self):
    assert(self.indexFile.table)

    for addr in self.indexFile.table:
      entry = EntryStore(self.fetchBytesForEntry(addr), self)
      self.entries.append(entry)

      if entry.next_addr:
        self.indexFile.table.append(CacheAddr(entry.next_addr))

  def fetchBytesForEntry(self, addr):
    block_file = addr.block_file
    block_number = addr.block_number
    num_blocks = addr.contiguous_blocks + 1
    
    entries = self.blockFiles[block_file].getEntry(block_number, num_blocks)
    return b"".join(entries)

  def insertAddrToIndex(self, addr):
    self.indexFile.table.append(CacheAddr(addr))

