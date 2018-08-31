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

from setuptools import setup, find_packages
setup(
    name="wowecon_make_training_dataset",
    version="0.3.3",
    namespace_packages=['wowecon'],
    packages=['wowecon','wowecon.training'],
    scripts=['make_training_dataset.py'],
    install_requires=['boto3==1.7.24',
                      'pytz==2018.4',
                      'humanfriendly==4.16.1'],
    package_data={
        '':['LICENSE']
        },
    author="Jon Moore",
    license="GPLv3",
    url="https://github.com/jonm/wow-econometrics"
)
