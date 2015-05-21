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
  fromDir = sys.argv[1]
  toDir = sys.argv[2]

  cm = CacheManager(fromDir, toDir)
  cm.processEntries()
  cm.outputToFiles()



main()
