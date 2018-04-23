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

import json
import logging
import os
import urllib

import itemcache
import iteminfo
import warmer
import wow

def _get_config():
    return { 'BUCKET_NAME' : os.environ.get('BUCKET_NAME'),
             'TABLE_NAME' : os.environ.get('TABLE_NAME'),
             'WOW_API_KEY' : os.environ.get('WOW_API_KEY') }

def prefetch(key, config=None):
    if config is None: config = _get_config()
    logging.warn("Prefetching key %s" % (key,))
    wow_client = wow.WoWCommunityAPIClient(config['WOW_API_KEY'])
    cache = itemcache.ItemInfoCache(config['TABLE_NAME'])
    caching_client = itemcache.CachingWoWCommunityAPIClient(wow_client, cache)
    retriever = iteminfo.ItemInfoRetriever(caching_client)
    w = warmer.ItemInfoCacheWarmer(config['BUCKET_NAME'], retriever)
    w.prefetch_iteminfo(key)

def handle(event, context):
    logging.warn("Event: %s" % (json.dumps(event, indent=4),))
    for sns_record in event['Records']:
        msg = sns_record['Sns']['Message']
        s3_event = json.loads(msg)
        for record in s3_event['Records']:
            prefetch(urllib.unquote(record['s3']['object']['key']))


