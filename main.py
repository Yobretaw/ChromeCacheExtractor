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

from manager import *


def main():
  pathToDir = "/Users/youkeshen/Desktop/Cache/"
  pathToIndex = "/Users/youkeshen/Desktop/Cache/index"

  cm = CacheManager(pathToDir)
  cm.processIndex()



main()

#from urllib.parse import urlparse

#print(urlparse("http://pos.baidu.com/wh/o.htm?ltr=http%3A%2F%2Ffitness.39.net%2Fspecial%2Fqtjs%2Findex.html&cf=u"))
