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

from disk_format import *


def main():
  #pathToIndex = "/Users/youkeshen/Library/Caches/Google/Chrome/Default/Cache/index"
  pathToDir = "/Users/youkeshen/Desktop/Cache/"
  pathToIndex = "/Users/youkeshen/Desktop/Cache/index"
  #pathToIndex = "/Users/youkeshen/Library/Application Support/Google/Chrome/Default/Application Cache/Cache/index"

  #index = Index(data=readFromFile(pathToIndex))
  cm = CacheManager(pathToDir)
  

def readFromFile(filepath):
  if not filepath:
    return None

  with open(filepath, 'rb') as f:
    return f.read()



main()
