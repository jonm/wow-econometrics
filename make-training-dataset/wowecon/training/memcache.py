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

import cPickle
import hashlib
import os
import random
import time

import humanfriendly

class IndexEntry:
    def __init__(self, key, value, etag=None, last_access=None):
        self.key = key
        self.value = value
        self.last_access = last_access
        self.etag = etag
        self.sizeb = 0L

class MemoryCache:
    def __init__(self, sizeb=None, hmax_size=None):
        if hmax_size is None and sizeb is None:
            raise ValueError("Must provide either hmax_size or sizeb")
        self._index = {}
        if sizeb is not None:
            self._max_sizeb = sizeb
        else:
            self._max_sizeb = humanfriendly.parse_size(hmax_size)
        self._total_sizeb = 0L
        self._num_keys = 0

    def get(self, key):
        if key not in self._index: return None
        self._index[key].last_access = time.time()
        return self._index[key].value

    def get_if_match(self, key, etag):
        if key not in self._index: return None
        if etag != self._index[key].etag: return None
        self._index[key].last_access = time.time()
        return self._index[key].value

    def _pick_random_key(self, avoid=None):
        k = random.choice(self._index.keys())
        while k == avoid:
            k = random.choice(self._index.keys())
        return k
    
    def _evict(self):
        if self._num_keys < 1: return

        if self._num_keys == 1:
            evict_key = self._index.keys()[0]
        else:
            k1 = self._pick_random_key()
            k2 = self._pick_random_key(avoid=k1)
            if self._index[k1].last_access < self._index[k2].last_access:
                evict_key = k1
            else:
                evict_key = k2

        self._total_sizeb -= self._index[evict_key].sizeb
        del self._index[evict_key]
        self._num_keys -= 1
                
    def put(self, key, value, etag=None):
        if key not in self._index:
            entry = IndexEntry(key, value, etag)
            self._index[key] = entry
            self._num_keys += 1

        pre_size = self._index[key].sizeb
            
        self._index[key].etag = etag
        self._index[key].last_access = time.time()
        self._index[key].sizeb = len(cPickle.dumps(value))

        self._total_sizeb = self._total_sizeb - pre_size + \
                            self._index[key].sizeb

        while self._total_sizeb > self._max_sizeb and self._total_sizeb > 0:
            self._evict()
