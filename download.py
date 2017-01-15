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
import subprocess

class DownloadManager:
    def __init__(self, wget='wget'):
        self.wget = wget

    def download(self, dest_dir, url):
        cwd = os.getcwd()
        try:
            os.chdir(dest_dir)
            # with -N, does If-Modified-Since
            if subprocess.call([self.wget, "-N", url]) != 0:
                raise Error("wget call failed")
            # with -c, does an If-Range query to continue a download
            if subprocess.call([self.wget, "-c", url]) != 0:
                raise Error("wget call failed")
        finally:
            os.chdir(cwd)
