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

import datetime

import boto3
from boto3.dynamodb.conditions import Key
import dateutil.parser
import pytz

class BatchRange:
    def __init__(self, global_table_name, index_table_name):
        ddb = boto3.resource('dynamodb')
        self._index_table = ddb.Table(index_table_name)
        self._global_table = ddb.Table(global_table_name)

    def get_datasets(self, d):
        resp = self._index_table.query(KeyConditionExpression =
                                       Key('date').eq(str(d)))
        out = map(lambda i: i['datetime'], resp['Items'])
        out.sort()
        return out

    def get_latest_dataset_before(self, dt=None):
        if dt is None: dt = datetime.datetime.now(pytz.utc)
    
        d = dt.date()
        while True:
            datasets = self.get_datasets(d)
            if len(datasets) > 0:
                datasets.reverse()
                for ds in datasets:
                    ds_dt = dateutil.parser.parse(ds + 'Z')
                    if ds_dt <= dt: return ds+'Z'
            d = d - datetime.timedelta(days=1)

    def get_earliest_dataset(self):
        resp = self._global_table.get_item(Key = { 'name' : 'earliest-batch' })
        return resp['Item']['value']

    def get_earliest_dataset_after(self, dt=None):
        dt0 = dateutil.parser.parse(self.get_earliest_dataset())
        if dt is None or dt < dt0:
            dt = dt0

        d = dt.date()
        while True:
            datasets = self.get_datasets(d)
            if len(datasets) > 0:
                for ds in datasets:
                    ds_dt = dateutil.parser.parse(ds + 'Z')
                    if ds_dt >= dt: return ds+'Z'
            d = d + datetime.timedelta(days=1)

    def get_latest_range(self, days=1):
        latest = self.get_latest_dataset_before()
        dt = dateutil.parser.parse(latest) - datetime.timedelta(days=days)
        earliest = self.get_earliest_dataset_after(dt)
        return (earliest, latest)


    
