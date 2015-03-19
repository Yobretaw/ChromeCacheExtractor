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

from disk_format import IndexHeader
from disk_format import Index
from disk_format import EntryStore

def main():
  pathToIndex = "/Users/youkeshen/Library/Caches/Google/Chrome/Default/Cache/index"

  index = Index(data=readFromFile(pathToIndex))
  

def readFromFile(filepath):
  if not filepath:
    return None

  with open(filepath, 'rb') as f:
    return f.read()



main()
