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

import struct

#from urllib.parse import urlparse
import urlparse
from MimeExt import *

def byte_to_int(b):
    #return int.from_bytes(b, byteorder='little')
    if len(b) == 1:
        return ord(struct.unpack("<c", b))[0]
    elif len(b) == 2:
        return struct.unpack("<h", b)[0]
    elif len(b) == 4:
        return struct.unpack("<i", b)[0]



def is_cache_initialized(addr):
    """
      Cache address is initialized if the first bit is set
    """
    #return (int.from_bytes(addr, byteorder='little') & 0x80000000) != 0
    return (byte_to_int(addr) & 0x80000000) != 0


def read_next_one_bytes_as_int(data, offset):
    return byte_to_int(data[offset : offset + 1])

def read_next_two_bytes_as_int(data, offset):
    return byte_to_int(data[offset : offset + 2])

def read_next_four_byte_as_int(data, offset):
    return byte_to_int(data[offset : offset + 4])

def read_next_x_bytes(data, offset, length):
    return data[offset : offset + length]

def get_extension(url, header):
    path = urlparse.urlparse(url)[2]

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

def parse_http_headers(text):
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


