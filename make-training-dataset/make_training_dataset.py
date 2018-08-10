#!/usr/bin/env python
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

import logging
import os

import dateutil.parser

import training

def main():
    global_table_name = os.environ['GLOBAL_TABLE_NAME']
    index_table_name = os.environ['INDEX_TABLE_NAME']
    src_bucket_name = os.environ['SRC_BUCKET_NAME']

    earliest = os.environ.get('EARLIEST_DATASET',None)
    if earliest is not None:
        earliest = dateutil.parser.parse(earliest)

    latest = os.environ.get('LATEST_DATASET',None)
    if latest is not None:
        latest = dateutil.parser.parse(latest)
        
    realm = os.environ.get('REALM','thrall')

    training.generate_training_data(global_table_name, index_table_name,
                                    src_bucket_name, earliest,
                                    latest, realm)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical("Uncaught exception", exc_info=True)
        raise e

        
