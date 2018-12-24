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

import datetime
import json
import logging
import time

import requests
from requests.auth import HTTPBasicAuth

class AuctionDataBatch:
    def __init__(self, url, last_modified):
        self.url = url
        self.last_modified = last_modified

    def __repr__(self):
        return "AuctionDataBatch(url=%s, last_modified=%s)" % (self.url.__repr__(),
                                                               self.last_modified.__repr__())
         

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
    def __init__(self, client_id, client_secret, endpoint='https://us.api.blizzard.com', oauth_endpoint='https://us.battle.net'):
        self._client_id = client_id
        self._client_secret = client_secret
        self._endpoint = endpoint
        self._oauth_endpoint = oauth_endpoint
        self._access_token = None
        self._token_expires = None

    def _get_access_token(self):
        if (self._access_token is not None
            and self._token_expires is not None
            and time.time() + 3600.0 < self._token_expires):
            return self._access_token

        resp = requests.post("%s/oauth/token" % (self._oauth_endpoint,),
                             auth = HTTPBasicAuth(self._client_id,
                                                  self._client_secret),
                             data = { 'grant_type' : 'client_credentials' })
        resp.raise_for_status()
        body = resp.json()
        if ('access_token' not in body
            or 'token_type' not in body or body['token_type'] != 'bearer'
            or 'expires_in' not in body):
            msg = "unexpected JSON body: %s" % json.dumps(body)
            logging.error(msg)
            raise ValueError(msg)
        self._access_token = body['access_token']
        self._token_expires = time.time() + body['expires_in']
        return self._access_token

    def get_auction_data_status(self, realm, locale='en_US'):
        uri = "%s/wow/auction/data/%s?locale=%s" % \
            (self._endpoint, realm, locale)
        headers = { 'Authorization' :
                    "Bearer %s" % (self._get_access_token(),) }

        start = time.time()
        logging.info("Fetching %s..." % uri)
        resp = requests.get(uri, headers = headers)
        end = time.time()
        logging.info("Fetch of %s complete (%ld ms)" % \
                            (uri, long((end - start) * 1000.0)))
        
        resp.raise_for_status()
        body = resp.json()
        if 'files' not in body:
            msg = "unexpected JSON body: %s" % json.dumps(body)
            logging.error(msg)
            raise ValueError(msg)
        out = []
        for obj in body['files']:
            if 'url' not in obj or 'lastModified' not in obj:
                msg = "unexpected JSON object: %s" % json.dumps(obj)
                logging.error(msg)
                raise ValueError(msg)
            lm = datetime.datetime.fromtimestamp(obj['lastModified'] / 1e3)
            out.append(AuctionDataBatch(obj['url'], lm))
        return out

    def get_item_info(self, item_id, locale='en_US'):
        uri = "%s/wow/item/%d?locale=%s" % \
            (self._endpoint, item_id, locale)
        headers = { 'Authorization' :
                    "Bearer %s" % (self._get_access_token(),) }

        resp = requests.get(uri, headers = headers)
        resp.raise_for_status()
        body = resp.json()
        if 'id' not in body:
            raise ValueError("no item ID in response")
        return ItemInfo(item_id, name = body.get("name"),
                        description = body.get("description"),
                        stackable = body.get("stackable"),
                        buy_price = body.get("buyPrice"),
                        sell_price = body.get("sellPrice"))


