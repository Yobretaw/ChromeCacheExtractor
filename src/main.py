import sys
from manager import *

def main():
    fromDir = sys.argv[1]
    toDir = sys.argv[2]

    cm = CacheManager(fromDir, toDir)
    cm.proceassEntries()
    cm.outputToFiles()

if __name__ == '__main__':
    main()
