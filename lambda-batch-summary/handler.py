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
import dateutil.parser

import summarize

def _get_config():
    return { 'SRC_BUCKET_NAME' : os.environ.get('SRC_BUCKET_NAME'),
             'DST_BUCKET_NAME' : os.environ.get('DST_BUCKET_NAME'),
             'BATCH_INDEX_TABLE_NAME' : os.environ.get('BATCH_INDEX_TABLE_NAME')
             }

def _record_batch(key, config):
    ddb = boto3.resource('dynamodb')
    table = ddb.Table(config['BATCH_INDEX_TABLE_NAME'])
    try:
        table.table_status
    except Exception as e:
        logging.warn("table_status", exc_info=True)
        table = ddb.create_table(
            TableName = config['BATCH_INDEX_TABLE_NAME'],
            KeySchema = [
                { 'AttributeName' : 'date', 'KeyType' : 'HASH' },
                { 'AttributeName' : 'datetime', 'KeyType' : 'RANGE' }
            ],
            AttributeDefinitions=[
                { 'AttributeName' : 'date', 'AttributeType' : 'S' },
                { 'AttributeName' : 'datetime', 'AttributeType' : 'S' }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            })
    
    dt_str = key.split("/")[-1]
    dt = dateutil.parser.parse(dt_str)
    table.put_item(Item = { 'date' : str(dt.date()), 'datetime' : dt_str })

def summarize_batch(key, config=None):
    if config is None: config = _get_config()
    logging.warn("Summarizing batch %s" % (key,))
    batch = summarize.load_auction_batch(config['SRC_BUCKET_NAME'],
                                         key)
    summary = summarize.summarize(batch)
    summarize.write_summary(config['DST_BUCKET_NAME'], key, summary)
    _record_batch(key, config)
    logging.warn("Wrote summary to %s/%s" % (config['DST_BUCKET_NAME'], key))

def _fn_last_modified(context):
    fn_name = context.function_name
    client = boto3.client('lambda')
    resp = client.get_function_configuration(FunctionName=fn_name)
    return dateutil.parser.parse(resp['LastModified'])

def _up_to_date(key, context, config=None):
    if config is None: config = _get_config()
    s3 = boto3.resource('s3')
    src_obj = s3.Object(config['SRC_BUCKET_NAME'], key)
    dst_obj = s3.Object(config['DST_BUCKET_NAME'], key)

    try:
        dst_lm = dst_obj.last_modified
    except:
        logging.warn("No last-modified on dst object %s" % (key,),
                     exc_info=True)
        return False

    src_lm = src_obj.last_modified
    logging.debug("dst_lm:%s src_lm:%s" %
                  (dst_lm.isoformat(), src_lm.isoformat()))
    if src_lm >= dst_lm: return False
    
    try:
        fn_lm = _fn_last_modified(context)
    except:
        logging.warn("_fn_last_modified", exc_info=True)
        return False
    
    logging.debug("dst_lm:%s fn_lm:%s" %
                  (dst_lm.isoformat(), fn_lm.isoformat()))
    return (dst_lm > fn_lm)

def handle(event, context):
    logging.warn("Event: %s" % (json.dumps(event, indent=4),))
    for sns_record in event['Records']:
        msg = sns_record['Sns']['Message']
        s3_event = json.loads(msg)
        for record in s3_event['Records']:
            key = urllib.unquote(record['s3']['object']['key'])
            if _up_to_date(key, context):
                logging.warn("Summary for batch %s is up to date" % (key,))
            else:
                summarize_batch(key)

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
