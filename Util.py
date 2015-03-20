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

def byteToInt(b):
  return int.from_bytes(b, byteorder='little')


def isCacheInitialized(addr):
  """
    Cache address is initialized if the first bit is set
  """
  #return (cacheAddr[0] | cacheAddr[1]) != 0
  return (int.from_bytes(addr, byteorder='little') & 0x80000000) != 0
