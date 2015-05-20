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

from urllib.parse import urlparse
from MimeExt import *

def byteToInt(b):
  return int.from_bytes(b, byteorder='little')


def isCacheInitialized(addr):
  """
    Cache address is initialized if the first bit is set
  """
  return (int.from_bytes(addr, byteorder='little') & 0x80000000) != 0


def readNextOneBytesAsInt(data, offset):
  return byteToInt(data[offset : offset + 1])

def readNextTwoBytesAsInt(data, offset):
  return byteToInt(data[offset : offset + 2])

def readNextFourBytesAsInt(data, offset):
  return byteToInt(data[offset : offset + 4])

def readNextXBytes(data, offset, length):
  return data[offset : offset + length]

def getExt(url, header):
  path = urlparse(url)[2]

  contentType = None
  if header.get('Content-Type'):
    contentType = header.get('Content-Type').split(";")[0]
  elif header.get('content-type'):
    contentType = header.get('content-type').split(";")[0]

  extFromUrl = path.split('.')[-1]
  extFromMimeType = mimeToExt.get(contentType)

  if not extFromMimeType:
    extFromMimeType = mimeToExt.get(contentType)

  if extToMime.get(extFromUrl):
    return "." + extFromUrl
  elif extFromMimeType:
    return "." + extFromMimeType
  else:
    return ""

def parseHTTPHeaders(text):
  text = text

  startPos = text.find(b'HTTP')
  endPos = text.find(b'\x00\x00', startPos)
  
  if not startPos:
    return None
  
  text = text[startPos:endPos].decode('utf-8')
  lineStr = text.split('\0')
  m = {}
  for line in lineStr:
    kvp = line.split(':')
    m[kvp[0].strip()] = kvp[1].strip() if len(kvp) > 1 else ''

  return lineStr, m


