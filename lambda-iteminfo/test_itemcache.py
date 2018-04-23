#!/usr/bin/env python
# Copyright (C) 2017, 2018 Jonathan Moore
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

import datetime
import unittest

import itemcache

class TestTable:
    def __init__(self):
        self.table_status = object()

class TestDynamoDb:
    def __init__(self, table):
        self._table = table

    def Table(self, _):
        return self._table

class TestItemInfoCache(unittest.TestCase):
    def setUp(self):
        self._table = TestTable()
        self._ddb = TestDynamoDb(self._table)
        self.impl = itemcache.ItemInfoCache('foo', dynamodb=self._ddb)

    def test_stable_item_is_fresh(self):
        now = datetime.datetime.now(itemcache._utc)
        one_day_ago = now - datetime.timedelta(days=1)
        twenty_days_ago = now - datetime.timedelta(days=20)
        item = { 'date' : one_day_ago.isoformat(),
                 'last_modified' : twenty_days_ago.isoformat() }
        self.assertTrue(self.impl._is_fresh(item, now=now))

    def test_recent_item_is_not_fresh(self):
        now = datetime.datetime.now(itemcache._utc)
        one_day_ago = now - datetime.timedelta(days=1)
        two_days_ago = now - datetime.timedelta(days=2)
        item = { 'date' : one_day_ago.isoformat(),
                 'last_modified' : two_days_ago.isoformat() }
        self.assertFalse(self.impl._is_fresh(item, now=now))

    def test_can_modify_heuristic(self):
        now = datetime.datetime.now(itemcache._utc)
        one_day_ago = now - datetime.timedelta(days=1)
        five_days_ago = now - datetime.timedelta(days=5)
        item = { 'date' : one_day_ago.isoformat(),
                 'last_modified' : five_days_ago.isoformat() }
        impl = itemcache.ItemInfoCache('foo', heuristic_freshness=0.33,
                                       dynamodb=self._ddb)
        self.assertTrue(impl._is_fresh(item, now=now))
        

if __name__ == "__main__":
    unittest.main()
