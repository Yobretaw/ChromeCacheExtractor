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
    self.separateFiles = []

    if pathToDir:
      self.indexFile = Index(pathToIndex=os.path.join(pathToDir, "index"))
      self.blockFiles[0] = Block(pathToBlock=os.path.join(pathToDir, "data_0"))
      self.blockFiles[1] = Block(pathToBlock=os.path.join(pathToDir, "data_1"))
      self.blockFiles[2] = Block(pathToBlock=os.path.join(pathToDir, "data_2"))
      self.blockFiles[3] = Block(pathToBlock=os.path.join(pathToDir, "data_3"))
