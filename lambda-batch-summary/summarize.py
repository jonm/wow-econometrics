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

import gzip
import json
import logging
import StringIO
import zlib

import boto3

DEFAULT_READ_BLOCK_SIZE = 8192

def _gzip_decompress(f):
    buf = StringIO.StringIO()
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    chunk = f.read(DEFAULT_READ_BLOCK_SIZE)
    while chunk:
        buf.write(d.decompress(chunk))
        chunk = f.read(DEFAULT_READ_BLOCK_SIZE)
    out = buf.getvalue()
    buf.close()
    return out

def load_auction_batch(bucket, key, s3=None):
    if s3 is None: s3 = boto3.resource('s3')
    obj = s3.Object(bucket, key)
    resp = obj.get()
    f = resp['Body']
    if 'ContentEncoding' in resp and resp['ContentEncoding'] == 'gzip':
        return json.loads(_gzip_decompress(f))
    return json.load(f)

def summarize(batch):
    items = {}
    for auc in batch['auctions']:
        item_id = auc['item']
        if auc['item'] not in items:
            items[item_id] = { 'item_id' : item_id,
                               'min_buyout' : None,
                               'total_volume' : 0 }

        qty = 1
        if 'quantity' in auc: qty = auc['quantity']

        if 'buyout' in auc:
            unit_price = int(auc['buyout'] * 1.0 / qty)
            if items[item_id]['min_buyout'] is None or unit_price < items[item_id]['min_buyout']:
                items[item_id]['min_buyout'] = unit_price

        items[item_id]['total_volume'] += qty
    return items

def write_summary(bucket, key, summary, s3=None):
    if s3 is None: s3 = boto3.resource('s3')

    buf = StringIO.StringIO()
    gzbuf = gzip.GzipFile(mode='wb',fileobj=buf)
    json.dump(summary, gzbuf, separators=(',',':'))
    gzbuf.close()
    
    obj = s3.Object(bucket, key)
    obj.put(Body = buf.getvalue(), ContentEncoding='gzip',
            ContentType = 'application/json')
    buf.close()
