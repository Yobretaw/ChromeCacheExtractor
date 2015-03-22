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

class CacheDumper(object):
    def __init__(self, pathToDir=None, overwrite=True):
        """
            Init cache manager
        """
        self.pathToDir = pathToDir
        self.size_first = 15
        self.size_second = 15
        self.overwrite = overwrite


    def init(self):
        if not self.checkDir():
            self.initDir()

    def initDir(self):
        """
            Generate cache directories
        """
        print("Cache directories does not exist or are damaged, recreating directories now...")

        if not os.path.exists(self.pathToDir):
            os.makedirs(self.pathToDir)

        for i in range(0, self.size_first + 1):
            dirpath = os.path.join(self.pathToDir, str(hex(i))[2:].zfill(1))
            if os.path.exists(dirpath):
                shutil.rmtree(dirpath)
                os.makedirs(dirpath)

            for j in range(0, self.size_second + 1):
                subdirpath = os.path.join(dirpath, str(hex(j))[2:].zfill(1))
                os.makedirs(subdirpath)

        print("Cache directories have been created successfully.")


    def checkDir(self):
        """
            Check if the cache directory alreay exists and has properly setup
            Return True if yes, otherwise return False
        """
        print("Checking cache directories...")
        if not os.path.exists(self.pathToDir):
            return False

        for i in range(0, self.size_first + 1):
            dirpath = os.path.join(self.pathToDir, str(hex(i))[2:].zfill(1))

            if not os.path.exists(dirpath):
                return False

            for j in range(0, self.size_second + 1):
                subdirpath = os.path.join(dirpath, str(hex(j))[2:].zfill(1))

                if not os.path.exists(subdirpath):
                    return False

        print("Cache directories already exists, continue...")
        return True


    def insert(self, url, content, isHeader=False, ext=None):
        """
            Insert entry to cache, return true if new entry is written into cache, false otherwise
        """
        key, dirpath, filepath = self.genPathFromUrl(url, isHeader, ext)

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        elif os.path.exists(filepath) and not self.overwrite:
            return False

        with open(filepath, 'wb') as tempfile:
            if isinstance(content, str):
              tempfile.write(bytes(content, 'utf-8'))
            else:
              tempfile.write(content)

        return True


    def fetch(self, url, isHeader=False):
        key, dirpath, filepath = self.genPathFromUrl(url, isHeader)
        if not os.path.exists(filepath):
            return None

        content = None
        with open(filepath, 'r') as tempfile:
            content = tempfile.read()

        return content

    def genPathFromUrl(self, url, isHeader, ext):
        m = hashlib.md5();
        m.update(url)
        key = m.hexdigest()

        first_dir, second_dir = key[0:1], key[1:2]
        dirpath = os.path.join(self.pathToDir, first_dir, second_dir, key)
        filepath = None
        #if isHeader:
        #  filepath = os.path.join(dirpath, "headers.txt")
        #else:
        #  filepath = os.path.join(dirpath, "content" + ext if ext else "")
        filepath = os.path.join(dirpath, "header.txt" if isHeader else ("content" + ext if ext else "content"))
        print(filepath)
        return key, dirpath, filepath
