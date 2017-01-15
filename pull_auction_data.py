#!/usr/bin/env python
#
# Copyright (C) 2017 Jonathan Moore
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

import os
import sys
import time

import battlenet
import download

def dest_dir_for(dt):
    return os.path.join(os.getcwd(), "data",
                        "%d" % dt.year, "%02d" % dt.month, "%02d" % dt.day, 
                        "%02d:%02d:%02d" % (dt.hour, dt.minute, dt.second))

def link_exists(path):
    try:
        os.lstat(path)
        return True
    except OSError:
        return False

def make_timestamped_link(dest_dir, dt, url):
    bn = os.path.basename(url)
    link_name = dt.isoformat() + "." + bn
    cwd = os.getcwd()
    try:
        os.chdir(dest_dir)
        if not link_exists(link_name):
            os.symlink(bn, link_name)
    finally:
        os.chdir(cwd)

def download_auction_data(api_key, realm='thrall'):
    client = battlenet.WoWCommunityAPIClient(api_key)
    dm = download.DownloadManager()
    for batch in client.get_auction_data_status(realm):
        dest_dir = dest_dir_for(batch.last_modified)
        if not os.access(dest_dir, os.F_OK):
            os.makedirs(dest_dir)
        dm.download(dest_dir, batch.url)
        make_timestamped_link(dest_dir, batch.last_modified, batch.url)

def main(realm='thrall', sleep_secs=300, n=None):
    if 'BATTLE_NET_API_KEY' not in os.environ:
        print >> sys.stderr, "Please set the BATTLE_NET_API_KEY environment variable."
        sys.exit(1)

    while True:
        download_auction_data(os.environ['BATTLE_NET_API_KEY'], realm)
        if n is not None: n -= 1
        if n is not None and n <= 0: break
        print "Waiting", sleep_secs, "seconds before next poll...",
        sys.stdout.flush()
        time.sleep(sleep_secs)
        print "done."

if __name__ == "__main__":
    main()

    
