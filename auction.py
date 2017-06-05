class Auction:
    time_ranges_minutes = { 'SHORT' : (0,30), 'MEDIUM' : (30,120),
                            'LONG' : (120, 720), 'VERY_LONG' : (720, 2880) }

    def __init__(self, auction_id=None, time_left=None, bid=None,
                 item_id=None, owner=None, buyout=None, quantity=None,
                 rand=None, seed=None, owner_realm=None, context=None):
        self.auction_id = auction_id
        self.time_left = time_left
        self.bid = bid
        self.item_id = item_id
        self.owner = owner
        self.buyout = buyout
        self.quantity = quantity
        self.rand = rand
        self.seed = seed
        self.owner_realm = owner_realm
        self.context = context

    @classmethod
    def from_dict(cls, d):
        return cls(auction_id = d.get('auc'),
                   time_left = d.get('timeLeft'),
                   bid = d.get('bid'),
                   item_id = d.get('item'),
                   owner = d.get('owner'),
                   buyout = d.get('buyout'),
                   quantity = d.get('quantity'),
                   rand = d.get('rand'),
                   seed = d.get('seed'),
                   owner_realm = d.get('ownerRealm'),
                   context = d.get('context'))

    def minutes_left_range(self):
        return self.time_ranges_minutes.get(self.time_left)

                 
