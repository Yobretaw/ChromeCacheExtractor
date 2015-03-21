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

from Util import *

class EntryStore(object):
  def __init__(self, data=None):
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

    if data:
      self.parse(data)

  def parse(self, data):
    offset = 0

    self.key_hash = readNextFourBytesAsInt(data, offset)
    offset += 4

    self.next_addr = readNextFourBytesAsInt(data, offset)
    offset += 4

    self.rankings_node = readNextFourBytesAsInt(data, offset)
    offset += 4

    self.reuse_count = readNextFourBytesAsInt(data, offset)
    offset += 4

    self.refetch_count = readNextFourBytesAsInt(data, offset)
    offset += 4

    self.state = readNextFourBytesAsInt(data, offset)
    offset += 4

    self.creation_time = byteToInt(readNextXBytes(data, offset, 8))
    offset += 8

    self.key_len = readNextFourBytesAsInt(data, offset)
    offset += 4

    self.long_key = readNextFourBytesAsInt(data, offset)
    offset += 4

    for i in range(0, len(self.data_size)):
      self.data_size[i] = readNextFourBytesAsInt(data, offset)
      offset += 4

    for i in range(0, len(self.data_addr)):
      self.data_addr[i] = readNextFourBytesAsInt(data, offset)
      offset += 4

    self.flags = readNextFourBytesAsInt(data, offset)
    offset += 4

    for i in range(0, len(self.pad)):
      self.data_addr[i] = readNextFourBytesAsInt(data, offset)
      offset += 4

    self.self_hash = readNextFourBytesAsInt(data, offset)
    offset += 4

    self.key = readNextXBytes(data, offset, self.key_len).decode('utf-8') if self.key_len <= 160 else None

    offset += int(256 - 24 * 4)
    print("-----------------------------------------------")
    print(self.key)
    print(self.long_key)
    print("-----------------------------------------------")

    #print(
    #  datetime.datetime.fromtimestamp(
    #    self.creation_time / 1e7
    #  ).strftime('%Y-%m-%d %H:%M:%S')
    #)
