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
import StringIO
import zlib

import boto3

DEFAULT_READ_BLOCK_SIZE = 8192

class ItemInfoCacheWarmer:
    def __init__(self, bucket_name, iteminfo_retriever, s3=None):
        self._bucket_name = bucket_name
        self._retriever = iteminfo_retriever
        if s3 is None: s3 = boto3.resource('s3')
        self._s3 = s3
        self._read_block_size = DEFAULT_READ_BLOCK_SIZE

    def _decompress(self, raw):
        out = StringIO.StringIO()
        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        chunk = raw.read(self._read_block_size)
        while chunk:
            out.write(d.decompress(chunk))
            chunk = raw.read(self._read_block_size)
        return out.getvalue()

    def prefetch_iteminfo(self, key_name):
        obj = self._s3.Object(self._bucket_name, key_name)
        resp = obj.get()
        f = resp['Body']
        if 'ContentEncoding' in resp and resp['ContentEncoding'] == 'gzip':
            batch = json.loads(self._decompress(f))
        else:
            batch = json.load(f)
        num = len(batch['auctions'])
        i = 0
        for auc in batch['auctions']:
            try:
                self._retriever.get_auction_item_info(auc)
            except Exception as e:
                logging.warn("Error on %s" % (json.dumps(auc, indent=4),),
                             exc_info=True)
            i += 1
            logging.info("%d/%d" % (i, num))

