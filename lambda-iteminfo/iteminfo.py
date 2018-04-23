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

import json
import logging

def _get_bonus_lists(auc):
    if 'bonusLists' not in auc: return []
    out = []
    for obj in auc['bonusLists']:
        if 'bonusListId' in obj:
            blid = obj['bonusListId']
            if blid not in out: out.append(blid)
    out.sort()
    return out

class ContextBonusListLookupException(Exception):
    pass

def _no_contexts(base):
    if 'availableContexts' not in base: return True
    cs = filter(lambda c: c, base['availableContexts'])
    return len(cs) == 0

class ItemInfoRetriever:
    def __init__(self, wow_client):
        self._client = wow_client

    def get_auction_item_info(self, auc):
        item_id = auc['item']
        base = self._client.get_item_info(item_id)
        if 'context' not in auc or auc['context'] == 0 or _no_contexts(base):
            return base

        # There is a context; we have to figure out which one we want.
        # The WoW Item API deals with context strings like 'world-quest-11'.
        # However, auctions come in with a numberical context ID.
        auc_bls = _get_bonus_lists(auc)

        if len(base['availableContexts']) == 1:
            context = base['availableContexts'][0]
            logging.warn("Found context %d = %s on item %s" % 
                         (auc['context'], context, item_id))
            return self._client.get_item_info(item_id, context=context,
                                              bonus_lists = auc_bls)

        for context in base['availableContexts']:
            ctx_info = self._client.get_item_info(item_id, context=context)
            default_bonus_lists = ctx_info['bonusSummary']['defaultBonusLists']
            matched = True
            for bl in default_bonus_lists:
                if bl not in auc_bls:
                    matched = False
                    break
            if matched:
                logging.warn("Found context %d = %s on item %s" % 
                             (auc['context'], context, item_id))
                return self._client.get_item_info(item_id, context=context,
                                                  bonus_lists = auc_bls)
        
        msg = ("Could not find context %d with bonus_lists=%s on item %d: %s" % (auc['context'], auc_bls, item_id, json.dumps(auc, indent=4)))
        logging.warn(msg)
        return base

