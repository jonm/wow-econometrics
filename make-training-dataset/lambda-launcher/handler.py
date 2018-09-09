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
import logging
import os
import re

import dateutil.parser

import launch
import range

def _configure_logging():
    loglevel_str = os.environ.get('LOG_LEVEL','logging.INFO')
    if re.match('^logging.[A-Z]+$', loglevel_str) is None:
        raise ValueError("Invalid logging level: %s" % (loglevel_str,))
    loglevel = eval(loglevel_str)
    logging.getLogger('').setLevel(loglevel)

def handle(event, context):
    _configure_logging()

    br = range.BatchRange(os.environ['GLOBAL_TABLE_NAME'],
                          os.environ['INDEX_TABLE_NAME'])

    days = int(os.environ.get('DAYS',1))

    earliest = os.environ.get('EARLIEST_DATASET')
    latest = os.environ.get('LATEST_DATASET')

    if earliest is None and latest is None:
        earliest, latest = br.get_latest_range(days)
    elif earliest is None:
        latest_dt = dateutil.parser.parse(latest)
        earliest_dt = latest_dt - datetime.timedelta(days=days)
        earliest = br.get_earliest_dataset_after(earliest_dt)
    elif latest is None:
        earliest_dt = dateutil.parser.parse(earliest)
        latest_dt = earliest_dt + datetime.timedelta(days=days)
        latest = br.get_latest_dataset_before(latest_dt)

    launch.run_instance(os.environ['MTD_VERSION'],
                        os.environ['GLOBAL_TABLE_NAME'],
                        os.environ['INDEX_TABLE_NAME'],
                        os.environ['SRC_BUCKET_NAME'],
                        os.environ['DST_BUCKET_NAME'],
                        earliest,
                        latest,
                        os.environ['AMI_ID'],
                        os.environ['KEYPAIR_NAME'],
                        [os.environ['SECURITY_GROUP_ID']],
                        os.environ['SUBNET_ID'],
                        os.environ['INSTANCE_TYPE'],
                        os.environ['IAM_INSTANCE_PROFILE_ARN'],
                        os.environ.get('FILECACHE_SIZE',None),
                        os.environ.get('MEMCACHE_SIZE',None))
    
    
