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

import logging
import os
import pprint

import boto3

def _generate_userdata(mtd_version, global_table_name, index_table_name,
                       src_bucket_name, dst_bucket_name, earliest_dataset,
                       latest_dataset, filecache_size=None,
                       memcache_size=None):
    template_path = os.path.join(os.environ.get('LAMBDA_TASK_ROOT','.'),
                                 'ec2-userdata.sh.template')
    ud0 = open(template_path,"r").read()
    ud1 = ud0.replace('%MTD_VERSION%', mtd_version)
    ud2 = ud1.replace('%GLOBAL_TABLE_NAME%', global_table_name)
    ud3 = ud2.replace('%INDEX_TABLE_NAME%', index_table_name)
    ud4 = ud3.replace('%SRC_BUCKET_NAME%', src_bucket_name)
    ud5 = ud4.replace('%DST_BUCKET_NAME%', dst_bucket_name)
    ud6 = ud5.replace('%EARLIEST_DATASET%', earliest_dataset)
    ud7 = ud6.replace('%LATEST_DATASET%', latest_dataset)

    if filecache_size is not None:
        ud8 = ud7.replace('%FILECACHE_SIZE%',
                          "export FILECACHE_SIZE=%s" % (filecache_size,))
    else:
        ud8 = ud7.replace('%FILECACHE_SIZE%','')

    if memcache_size is not None:
        ud9 = ud8.replace('%MEMCACHE_SIZE%',
                          "export MEMCACHE_SIZE=%s" % (memcache_size,))
    else:
        ud9 = ud8.replace('%MEMCACHE_SIZE%','')

    logging.debug("userdata =\n%s" % (ud9,))
        
    return ud9

def run_instance(mtd_version, global_table_name, index_table_name,
                 src_bucket_name, dst_bucket_name, earliest_dataset,
                 latest_dataset, ami_id, keypair_name, security_group_ids,
                 subnet_id, instance_type, iam_instance_profile_arn,
                 filecache_size=None, memcache_size=None):

    userdata = _generate_userdata(mtd_version, global_table_name,
                                  index_table_name, src_bucket_name,
                                  dst_bucket_name, earliest_dataset,
                                  latest_dataset,
                                  filecache_size=filecache_size,
                                  memcache_size=memcache_size)
    
    client = boto3.client('ec2')
    resp = client.run_instances(
        ImageId=ami_id,
        MaxCount=1,
        MinCount=1,
        InstanceType=instance_type,
        KeyName=keypair_name,
        SecurityGroupIds=security_group_ids,
        SubnetId=subnet_id,
        UserData=userdata,
        IamInstanceProfile={'Arn':iam_instance_profile_arn},
        TagSpecifications=[
            { 'ResourceType':'instance',
              'Tags':[
                  { 'Key': 'application', 'Value': 'wowecon' },
                  { 'Key': 'role', 'Value': 'wowecon-make-training-dataset' }
              ]
            }
        ])
    logging.info("results of launch:\n%s" % (pprint.pformat(resp),))
    
