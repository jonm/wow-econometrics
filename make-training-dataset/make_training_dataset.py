#!/usr/bin/env python
#
# Copyright (C) 2018 Jonathan Moore
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
import tempfile

import dateutil.parser

from wowecon.training import filecache
from wowecon.training import memcache
from wowecon.training import training

def _configure_logging():
    loglevel_str = os.environ.get('LOG_LEVEL','logging.INFO')
    if not loglevel_str.startswith('logging.'):
        raise ValueError("Invalid logging level: %s" % (loglevel_str,))
    loglevel = eval(loglevel_str)

    fmt = '%(asctime)s %(levelname)-8s %(message)s'
    formatter = logging.Formatter(fmt)
    
    logfile = os.environ.get('LOG_TO')
    if logfile is not None:
        logging.basicConfig(filename=logfile, format=fmt, level=loglevel)

        console = logging.StreamHandler()
        console.setLevel(loglevel)
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
    else:
        logging.basicConfig(format=fmt, level=loglevel)
        
def main():
    _configure_logging()
    global_table_name = os.environ['GLOBAL_TABLE_NAME']
    index_table_name = os.environ['INDEX_TABLE_NAME']
    src_bucket_name = os.environ['SRC_BUCKET_NAME']
    dst_bucket_name = os.environ['DST_BUCKET_NAME']

    fcache = None
    fcache_size = os.environ.get('FILECACHE_SIZE',None)
    if fcache_size is not None:
        fcache = filecache.FileCache(hmax_size=fcache_size)

    mcache = None
    mcache_size = os.environ.get('MEMCACHE_SIZE',None)
    if mcache_size is not None:
        mcache = memcache.MemoryCache(hmax_size=mcache_size)
        
    earliest = os.environ.get('EARLIEST_DATASET',None)
    if earliest is not None:
        earliest = dateutil.parser.parse(earliest)

    latest = os.environ.get('LATEST_DATASET',None)
    if latest is not None:
        latest = dateutil.parser.parse(latest)
        
    realm = os.environ.get('REALM','thrall')

    if fcache is None:
        training.generate_training_data(global_table_name, index_table_name,
                                        src_bucket_name, dst_bucket_name,
                                        earliest, latest,
                                        realm, fcache, mcache)
    else:
        with fcache as fc:
            training.generate_training_data(global_table_name, index_table_name,
                                            src_bucket_name, dst_bucket_name,
                                            earliest, latest, realm,
                                            fc, mcache)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical("Uncaught exception", exc_info=True)
        raise e

        
