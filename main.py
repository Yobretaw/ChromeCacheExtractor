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
    fromDir = "/Users/youkeshen/Desktop/Cache/"
    toDir = "/Users/youkeshen/Desktop/Results/"

    cm = CacheManager(fromDir, toDir)
    cm.processEntries()
    cm.outputToFiles()



main()
