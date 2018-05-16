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

import boto3
import uuid

def s3_touch(bucket, key):
    client = boto3.client('s3')
    resp = client.head_object(Bucket = bucket, Key = key)
    metadata = resp['Metadata']
    name = str(uuid.uuid4())
    while name in metadata:
        name = str(uuid.uuid4())
    metadata[name] = str(uuid.uuid4())
    
    client.copy_object(Bucket = bucket, Key = key,
                       CopySource = "%s/%s" % (bucket, key),
                       Metadata = metadata,
                       MetadataDirective='REPLACE')
    del metadata[name]
    client.copy_object(Bucket = bucket, Key = key,
                       CopySource = "%s/%s" % (bucket, key),
                       Metadata = metadata,
                       MetadataDirective='REPLACE')
    
