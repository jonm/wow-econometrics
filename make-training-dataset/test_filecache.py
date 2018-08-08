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

import subprocess
import unittest
import uuid

from filecache import FileCache

class TestFileCache(unittest.TestCase):
    def test_creation(self):
        FileCache(sizeb=1024)

    def test_creation_human_friendly_size(self):
        FileCache(hmax_size="10k")

    def test_cache_hit(self):
        with FileCache(hmax_size="10k") as fc:
           s = str(uuid.uuid4())
           fc.put("k", s)
           with fc.get("k") as in_f:
               self.assertEquals(s, in_f.read())

    def test_cache_eviction(self):
        v = "s" * 1000
        with FileCache(sizeb="10k") as fc:
            for _ in xrange(10):
                fc.put(str(uuid.uuid4()), v)
            for _ in xrange(5):
                fc.put(str(uuid.uuid4()), v)
            subprocess.call(["du","-b","-s",fc._directory])
               
if __name__ == "__main__":
    unittest.main()
