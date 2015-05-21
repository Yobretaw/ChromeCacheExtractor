# Chrome Cache Extractor
A utility that parses Google Chrome's cache files. Current implementation follows Chrome Disk Cache 2.x. See [Chrome DiskCache](https://www.chromium.org/developers/design-documents/network-stack/disk-cache)

## Usage
    $ cd src/
    $ python main.py <cache_dir> <output_dir>

Cache directory can be found [here](https://www.chromium.org/user-experience/user-data-directory). Note the cache directory should have these files: **index**, **data_n** and **f\_xxxxxx**.

## Requirement
  - Python 2.7

## Issue
Please report any bugs or requests that you have.

## License
The code is released under MIT License. See LICENSE file for details.
