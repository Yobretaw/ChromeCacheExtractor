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

class EntryStore(object):
  def __init__(self, data=None):
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

    if data:
      self.parse(data)

  def pares(self, data):
    pass
