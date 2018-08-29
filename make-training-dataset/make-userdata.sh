#!/bin/bash
#
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

if [ -z "$MTD_VERSION" ]; then
    echo "Please set the MTD_VERSION environment variable."
    exit 1
fi
if [ -z "$GLOBAL_TABLE_NAME" ]; then
    echo "Please set the GLOBAL_TABLE_NAME environment variable."
    exit 1
fi
if [ -z "$INDEX_TABLE_NAME" ]; then
    echo "Please set the INDEX_TABLE_NAME environment variable."
    exit 1
fi
if [ -z "$SRC_BUCKET_NAME" ]; then
    echo "Please set the SRC_BUCKET_NAME environment variable."
    exit 1
fi
if [ -z "$DST_BUCKET_NAME" ]; then
    echo "Please set the DST_BUCKET_NAME environment variable."
    exit 1
fi
if [ -z "$EARLIEST_DATASET" ]; then
    echo "Please set the EARLIEST_DATASET environment variable."
    exit 1
fi
if [ -z "$LATEST_DATASET" ]; then
    echo "Please set the LATEST_DATASET environment variable."
    exit 1
fi
if [ -z "$FILECACHE_SIZE" ]; then
    FC=
else
    FC="export FILECACHE_SIZE=$FILECACHE_SIZE"
fi

cat ec2-userdata.sh.template | \
    sed -e "s/%MTD_VERSION%/$MTD_VERSION/g" | \
    sed -e "s/%GLOBAL_TABLE_NAME%/$GLOBAL_TABLE_NAME/g" | \
    sed -e "s/%INDEX_TABLE_NAME%/$INDEX_TABLE_NAME/g" | \
    sed -e "s/%SRC_BUCKET_NAME%/$SRC_BUCKET_NAME/g" | \
    sed -e "s/%DST_BUCKET_NAME%/$DST_BUCKET_NAME/g" | \
    sed -e "s/%EARLIEST_DATASET%/$EARLIEST_DATASET/g" | \
    sed -e "s/%LATEST_DATASET%/$LATEST_DATASET/g" | \
    sed -e "s/%FILECACHE_SIZE%/$FC/g" \
	> ec2-userdata.sh
