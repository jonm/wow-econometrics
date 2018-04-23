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

import httplib
import logging

import requests

class WoWCommunityAPIClient:
    def __init__(self, api_key, endpoint='https://us.api.battle.net'):
        self._api_key = api_key
        self._endpoint = endpoint

    def get_item_info(self, item_id, locale='en_US', context=None,
                      bonus_lists=[]):
        if not context:
            uri = "%s/wow/item/%d?locale=%s&apikey=%s" % \
                (self._endpoint, item_id, locale, self._api_key)
        elif len(bonus_lists) == 0:
            uri = "%s/wow/item/%d/%s?locale=%s&apikey=%s" % \
                (self._endpoint, item_id, context, locale, self._api_key)
        else:
            uri = "%s/wow/item/%d/%s?bl=%s&locale=%s&apikey=%s" % \
                (self._endpoint, item_id, context,
                 ','.join(map(lambda i: str(i), bonus_lists)),
                 locale, self._api_key)

        resp = requests.get(uri)
        resp.raise_for_status()

        body = resp.json()
        if 'id' not in body:
            raise ValueError("no item ID in response")
        return body


