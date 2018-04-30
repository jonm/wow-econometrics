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

import boto3

import summarize

def _get_config():
    return { 'SRC_BUCKET_NAME' : os.environ.get('SRC_BUCKET_NAME'),
             'DST_BUCKET_NAME' : os.environ.get('DST_BUCKET_NAME') }

def summarize_batch(key, config=None):
    if config is None: config = _get_config()
    logging.warn("Summarizing batch %s" % (key,))
    batch = summarize.load_auction_batch(config['SRC_BUCKET_NAME'],
                                         key)
    summary = summarize.summarize(batch)
    summarize.write_summary(config['DST_BUCKET_NAME'], key, summary)
    logging.warn("Wrote summary to %s/%s" % (config['DST_BUCKET_NAME'], key))

def handle(event, context):
    logging.warn("Event: %s" % (json.dumps(event, indent=4),))
    for sns_record in event['Records']:
        msg = sns_record['Sns']['Message']
        s3_event = json.loads(msg)
        for record in s3_event['Records']:
            summarize_batch(urllib.unquote(record['s3']['object']['key']))

def republish_event(key, topic):
    event = { 'Records' :
                  [ { 's3' : 
                      { 'object' : 
                        { 'key' : urllib.quote(key) } } } ] }
    topic.publish(Message = json.dumps(event))
    logging.warn("Published event for key %s" % (key,))
    

def republish_events(src_bucket, sns_topic_arn):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(src_bucket)
    sns = boto3.resource('sns')
    topic = sns.Topic(sns_topic_arn)
    for obj in bucket.objects.all():
        republish_event(obj.key, topic)
