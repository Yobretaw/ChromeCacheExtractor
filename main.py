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
