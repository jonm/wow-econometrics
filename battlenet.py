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

import datetime
import json
import logging

import requests

class AuctionDataBatch:
    def __init__(self, url, last_modified):
        self.url = url
        self.last_modified = last_modified

class ItemInfo:
    def __init__(self, item_id, name = None, description = None,
                 stackable = None, buy_price = None, sell_price = None):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.stackable = stackable
        self.buy_price = buy_price
        self.sell_price = sell_price

    def __repr__(self):
        return "ItemInfo(%d, name=%s, description=%s, stackable=%s, buy_price=%s, sell_price=%s)" % \
            (self.item_id, self.name.__repr__(),
             self.description.__repr__(), self.stackable.__repr__(),
             self.buy_price.__repr__(), self.sell_price.__repr__())

    def __str__(self):
        return "<ItemInfo:#%d:%s>" % (self.item_id, self.name)
                 

class WoWCommunityAPIClient:
    def __init__(self, api_key, endpoint='https://us.api.battle.net'):
        self._api_key = api_key
        self._endpoint = endpoint

    def get_auction_data_status(self, realm, locale='en_US'):
        uri = "%s/wow/auction/data/%s?locale=%s&apikey=%s" % \
            (self._endpoint, realm, locale, self._api_key)
        resp = requests.get(uri)
        resp.raise_for_status()
        body = resp.json()
        if 'files' not in body:
            raise ValueError("unexpected JSON body: %s" % json.dumps(body))
        out = []
        for obj in body['files']:
            if 'url' not in obj or 'lastModified' not in obj:
                raise ValueError("unexpected JSON object: %s" % json.dumps(obj))
            lm = datetime.datetime.fromtimestamp(obj['lastModified'] / 1e3)
            out.append(AuctionDataBatch(obj['url'], lm))
        return out

    def get_item_info(self, item_id, locale='en_US'):
        uri = "%s/wow/item/%d?locale=%s&apikey=%s" % \
            (self._endpoint, item_id, locale, self._api_key)
        resp = requests.get(uri)
        resp.raise_for_status()
        body = resp.json()
        if 'id' not in body:
            raise ValueError("no item ID in response")
        return ItemInfo(item_id, name = body.get("name"),
                        description = body.get("description"),
                        stackable = body.get("stackable"),
                        buy_price = body.get("buyPrice"),
                        sell_price = body.get("sellPrice"))


