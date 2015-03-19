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

import binascii

# https://chromium.googlesource.com/chromium/src.git/+/master/net/disk_cache/blockfile/disk_format.h

kIndexTablesize = 0x10000
kIndexMagic = 0xC103CAC3
kCurrentVersion = 0x20000

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
    #hexval = ""
    #for b in data:
    #  hexval += "{0:b}".format(b)

    #print(type(hexval))
    #print(type(data))
    #print(data)

    self.offset = 0
    self.magic = int.from_bytes(data[self.offset:self.offset+4], byteorder='little')
    self.offset += 4
    self.version = int.from_bytes(data[self.offset:self.offset+4], byteorder='little')
    self.offset += 4
    self.num_entries = int.from_bytes(data[self.offset:self.offset+4], byteorder='little')
    self.offset += 4
    self.num_bytes = int.from_bytes(data[self.offset:self.offset+4], byteorder='little')
    self.offset += 4
    self.last_file = int.from_bytes(data[self.offset:self.offset+4], byteorder='little')
    self.offset += 4
    self.this_id = int.from_bytes(data[self.offset:self.offset+4], byteorder='little')    
    self.offset += 4
    self.stats = int.from_bytes(data[self.offset:self.offset+4], byteorder='little')      
    self.offset += 4
    self.table_len = int.from_bytes(data[self.offset:self.offset+4], byteorder='little')  
    self.offset += 4
    self.crash = int.from_bytes(data[self.offset:self.offset+4], byteorder='little')      
    self.offset += 4
    self.experiment = int.from_bytes(data[self.offset:self.offset+4], byteorder='little') 
    self.offset += 4
    self.create_time = int.from_bytes(data[self.offset:self.offset+8], byteorder='little')
    self.offset += 8

    # ignore LruData
    self.offset = 352


class LruData(object):
  def __init__(self):
    pass



class Index(object):
  def __init__(self, data=None):
    self.header = None
    self.table = None
    self.data = None

    self.offset = 0

    if data:
      self.data = data
      self.parse(self.data)

  def parse(self, data):
    self.header = IndexHeader(headData=self.data)
    self.offset = self.header.offset

    self.table = [0] * self.header.table_len
    for i in range(0, self.header.table_len):
      self.table[i] = int.from_bytes(self.data[self.offset: self.offset+4], byteorder='little')
      self.offset += 4

    print(self.table)



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
