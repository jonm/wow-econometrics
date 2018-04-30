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
import hashlib
import logging
import json
import sys

import boto3
import dateutil.parser

class UTC(datetime.tzinfo):
    def utcoffset(self, dt): return datetime.timedelta(0)
    def tzname(self, dt): return 'UTC'
    def dst(self, dt): return datetime.timedelta(0)

_utc = UTC()

class ItemInfoCache:
    def __init__(self, dynamodb_table_name, heuristic_freshness=0.1,
                 dynamodb=None):
        self._table_name = dynamodb_table_name
        self._heuristic_freshness = heuristic_freshness
        if dynamodb is None:
            dynamodb = boto3.resource('dynamodb')
        self._table = dynamodb.Table(self._table_name)
        
        try:
            self._table.table_status
        except Exception as e:
            logging.warn(str(e))
            self._table = dynamodb.create_table(
                TableName = self._table_name,
                KeySchema = [
                    { 'AttributeName' : 'iteminfo_id',
                      'KeyType': 'HASH' }
                ],
                AttributeDefinitions=[
                    { 'AttributeName' : 'iteminfo_id',
                      'AttributeType': 'S' }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                })

    def _get_iteminfo_id(self, item_id, context, bonus_lists):
        if context is None: context = ""
        return "%d:%s:%s" % (item_id, context,
                             ','.join(map(lambda bl: str(bl), bonus_lists)))

    def _is_fresh(self, item, now=None):
        if now is None:
            now = datetime.datetime.now(_utc)
        if 'date' not in item or 'last_modified' not in item:
            return False

        fetched = dateutil.parser.parse(item['date'])
        last_modified = dateutil.parser.parse(item['last_modified'])
        stable_for = now - last_modified
        portion = int(1.0 / self._heuristic_freshness)
        return (now - fetched) < (stable_for / portion)

    def lookup(self, item_id, context=None, bonus_lists=[]):
        key = self._get_iteminfo_id(item_id, context, bonus_lists)
        item = None

        resp = self._table.get_item(Key = { 'iteminfo_id' : key })
        if resp is None or 'Item' not in resp:
            return None
        item = resp['Item']
        
        if self._is_fresh(item):
            try:
                return json.loads(item['body'])
            except KeyError, ValueError:
                return None
        else:
            return None

    def update(self, item_id, info, context=None, bonus_lists=[]):
        key = self._get_iteminfo_id(item_id, context, bonus_lists)
        now = datetime.datetime.now(_utc)
        body = json.dumps(info, separators=(',',':'), sort_keys=True)

        item = None
        resp = self._table.get_item(Key = { 'iteminfo_id' : key })
        if resp is not None and 'Item' in resp:
            item = resp['Item']

        if item is not None and item['body'] == body:
            item['date'] = now.isoformat()
            self._table.put_item(Item = item)
        else:
            self._table.put_item(
                Item = { 'iteminfo_id' : key,
                         'body' : body,
                         'date' : now.isoformat(),
                         'last_modified' : now.isoformat() })

class CachingWoWCommunityAPIClient:
    def __init__(self, wow_client, iteminfo_cache):
        self._client = wow_client
        self._cache = iteminfo_cache

    def get_item_info(self, item_id, locale='en_US', context=None,
                      bonus_lists=[]):
        logging.debug("CachingWoWCommunityAPIClient.get_item_info: getting %s" % item_id)
        cache_hit = self._cache.lookup(item_id, context, bonus_lists)
        if cache_hit is not None: return cache_hit

        info = self._client.get_item_info(item_id, locale, context, bonus_lists)
        self._cache.update(item_id, info, context, bonus_lists)
        return info
