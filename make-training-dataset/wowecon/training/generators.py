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
import json
import logging
import StringIO
import zlib

import boto3
from boto3.dynamodb.conditions import Key
import dateutil.parser
import pytz

def get_earliest_dataset(global_table_name):
    ddb = boto3.resource('dynamodb')
    global_table = ddb.Table(global_table_name)
    resp = global_table.get_item(Key = { 'name' : 'earliest-batch' })
    return dateutil.parser.parse(resp['Item']['value'])

def gen_dates(earliest, latest=None):
    if latest is None: latest = datetime.datetime.now(pytz.utc)
    end = latest.date()
    cur = earliest.date()
    while cur <= end:
        yield cur
        cur = cur + datetime.timedelta(days=1)

def get_datasets(index_table_name, d):
    ddb = boto3.resource('dynamodb')
    index_table = ddb.Table(index_table_name)
    resp = index_table.query(KeyConditionExpression = Key('date').eq(str(d)))
    out = map(lambda i: i['datetime'], resp['Items'])
    out.sort()
    return out

def gen_datasets(index_table_name, earliest, latest=None):
    if latest is None: latest = datetime.datetime.now(pytz.utc)
    for d in gen_dates(earliest, latest):
        for dataset in get_datasets(index_table_name, d):
            when = dateutil.parser.parse(dataset + 'Z')
            if when >= earliest and when <= latest:
                yield dataset

def _gzip_decompress(f):
    DEFAULT_READ_BLOCK_SIZE = 8192
    buf = StringIO.StringIO()
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    chunk = f.read(DEFAULT_READ_BLOCK_SIZE)
    while chunk:
        buf.write(d.decompress(chunk))
        chunk = f.read(DEFAULT_READ_BLOCK_SIZE)
    out = buf.getvalue()
    buf.close()
    return out

def load_summary(bucket_name, dataset, realm='thrall'):
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_name, "%s/%s" % (realm, dataset))
    resp = obj.get()
    f = resp['Body']
    if 'ContentEncoding' in resp and resp['ContentEncoding'] == 'gzip':
        return json.loads(_gzip_decompress(f))
    return json.load(f)

def get_training_data_columns():
    return ('item_id', 'year1', 'month1', 'day1', 'weekday1',
            'hour1', 'minute1', 'second1',
            'volume1', 'price1',
            'year2', 'month2', 'day2', 'weekday2',
            'hour2', 'minute2', 'second2',
            'volume2', 'price2')

def gen_observations(dt1, summary1, dt2, summary2):
    logging.info("Generating observations from %s -> %s" %
                 (dt1.isoformat(), dt2.isoformat()))
    for record in summary1.values():
        item_id = record['item_id']
        if str(item_id) in summary2:
            record2 = summary2[str(item_id)]
            yield (item_id, dt1.year, dt1.month, dt1.day, dt1.weekday(),
                   dt1.hour, dt1.minute, dt1.second,
                   record['total_volume'], record['min_buyout'],
                   dt2.year, dt2.month, dt2.day, dt2.weekday(),
                   dt2.hour, dt2.minute, dt2.second,
                   record2['total_volume'], record2['min_buyout'])

def gen_observations_from(index_table_name, bucket_name,
                          dataset, realm='thrall'):
    s1 = load_summary(bucket_name, dataset, realm)
    dt1 = dateutil.parser.parse(dataset + 'Z')
    latest = dt1 + datetime.timedelta(days=2) # 48 hrs
    for dataset2 in gen_datasets(index_table_name,
                                 dt1 + datetime.timedelta(microseconds=1),
                                 latest):
        s2 = load_summary(bucket_name, dataset2, realm)
        dt2 = dateutil.parser.parse(dataset2 + 'Z')
        for obs in gen_observations(dt1, s1, dt2, s2):
            yield obs

def gen_all_observations(global_table_name, index_table_name, bucket_name,
                         earliest=None, latest=None, realm='thrall'):
    if earliest is None:
        earliest = get_earliest_dataset(global_table_name)

    yield get_training_data_columns() # header row

    for dataset in gen_datasets(index_table_name, earliest, latest):
        for obs in gen_observations_from(index_table_name, bucket_name,
                                         dataset, realm):
            yield obs
