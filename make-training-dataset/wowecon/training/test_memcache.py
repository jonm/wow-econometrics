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

import unittest
import uuid

from memcache import MemoryCache

class TestMemoryCache(unittest.TestCase):
    def test_creation(self):
        MemoryCache(sizeb=1024)

    def test_creation_human_friendly_size(self):
        MemoryCache(hmax_size="10k")

    def test_cache_hit(self):
        mc = MemoryCache(hmax_size="10k")
        s = str(uuid.uuid4())
        mc.put("k", s)
        self.assertEquals(s, mc.get("k"))

    def test_cache_eviction(self):
        v = "s" * 1000
        mc = MemoryCache(hmax_size="10k")
        for _ in xrange(10):
            mc.put(str(uuid.uuid4()), v)
        for _ in xrange(5):
            mc.put(str(uuid.uuid4()), v)
               
if __name__ == "__main__":
    unittest.main()
