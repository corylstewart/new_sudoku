from google.appengine.ext import ndb
import datetime

class Positions(ndb.Model):
    uid = ndb.StringProperty()
    stock = ndb.StringProperty()
    position = ndb.PickleProperty()
    vols = ndb.PickleProperty()
    rate = ndb.FloatProperty()
    created = ndb.DateTimeProperty(auto_now_add = True)

    def save_position(self, uid, stock, position, vols, rate):
        pos = Positions(uid = uid,
                       stock = stock,
                       position = position,
                       vols = vols,
                       rate = rate)
        position_key = pos.put()
        return position_key

    def retrieve_position(self, uid, stock):
        position = Positions.query(Positions.uid == uid, Positions.stock == stock).order(-Positions.created)
        if position.count() > 0:
            for p in position:
                return p
        return False


class OptionChain(ndb.Model):
    stock = ndb.StringProperty()
    option_chain = ndb.PickleProperty()
    created = ndb.DateTimeProperty(auto_now = True)

    def save_option_chain(self, stock, option_chain):
        chain = OptionChain(stock = stock,
                            option_chain = option_chain)
        chain_key = chain.put()
        return chain_key

    def retieve_option_chain(self, stock):
        chain = OptionChain.query(OptionChain.stock == stock)
        if chain.count() > 0:
            for c in chain:
                return c
        return False