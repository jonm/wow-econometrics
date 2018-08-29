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
import logging
import time

import boto3
import pytz
from s3transfer.manager import TransferManager

import streaming
import generators

def tuple2csv(t):
    """Note: assumes no values in t need escaping."""
    return ''.join((','.join(map(str,t)),'\r\n'))

def line_generator(tuple_generator):
    for t in tuple_generator:
        yield tuple2csv(t)

def generate_training_data(global_table_name, index_table_name,
                           src_bucket_name, dst_bucket_name,
                           earliest=None, latest=None, realm='thrall',
                           filecache=None):
    s3 = boto3.client('s3')
    tm = TransferManager(s3)
    extra_args = { 'ACL' : 'private',
                   'ContentType' : 'text/csv' }

    g = generators.Generator(global_table_name, index_table_name,
                             src_bucket_name, realm, filecache)
    generator = g.gen_all_observations(earliest, latest)
    stream = streaming.StreamingSource(line_generator(generator))

    start = datetime.datetime.now(pytz.utc)
    key = "%s/%s.csv" % (realm, start.isoformat())

    logging.info("Beginning generation of dataset s3://%s/%s" %
                 (dst_bucket_name, key))
    f = tm.upload(stream, dst_bucket_name, key, extra_args = extra_args)
    f.result()
    end = datetime.datetime.now(pytz.utc)
    logging.info("Dataset s3://%s/%s generation complete (%s)" % 
                 (dst_bucket_name, key, (end - start)))

    
                           
