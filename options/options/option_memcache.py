import time
import datetime
import copy
from google.appengine.api import memcache

class PositionMemcache:
    'this class manages set and reading the position in the memcache'

    def __init__(self, user = 'base', stock_symbol = ''):
        self.user = user
        self.stock_symbol = stock_symbol

    #creates a basic template for the memcache reading
    def get_blank(self, kind):
        return memcache.get(self.user + '_' + self.stock_symbol + '_' + kind)

    #gets the position from memcache returns none if not found
    def get_position(self):
        return self.get_blank('position')

    #gets the expiration vols from memcache returns none if not found
    def get_vols(self):
        return self.get_blank('vols')

    #gets the projected dividends from memcache returns none if not found
    def get_projected_dividends(self):
        return self.get_blank('projected_dividends')

    #gets the past dividends from memcache returns none if not found
    def get_past_dividends(self):
        return self.get_blank('past_dividends')

    #gets the option chain from memcache returns none if not found
    def get_option_chain(self):
        return memcache.get(self.stock_symbol + '_option_chain')

    #gets the occ listed stock from memcache returns none if not found
    def get_occ_listed_stocks(self):
        return memcache.get('occ_listed_stocks')

    #defines a basic template for writing to the memcache
    def set_blank(self, kind, value):
        memcache.set(self.user + '_' + self.stock_symbol + '_' + kind, value)

    #sets the postion in the memcache
    def set_position(self, position):
        self.set_blank('position', position)

    #sets the expiration vols in the memcache
    def set_vols(self, vols):
        self.set_blank('vols', vols)

    #sets the past dividends in the memcache
    def set_past_dividends(self, past_dividends):
        self.set_blank('past_dividends', past_dividends)

    #sets the projected dividends in the memcache
    def set_projected_divideds(self, projected_dividends):
        self.set_blank('projected_dividends', projected_dividends)

    #sets the option chain in the memcache with a 7 hour time limit
    def set_option_chain(self, option_chain):
        memcache.set(self.stock_symbol + '_option_chain', option_chain, 25200)

    #sets the occ list in the memcache with a 7 hour time limit
    def set_occ_listed_stocks(self, occ_listed_stocks):
        memcache.set('occ_listed_stocks', occ_listed_stocks, 25200)

    #defines the basic template for deleting a item from memcache
    def delete_blank(self, kind):
        memcache.delete(self.user + '_' + self.stock_symbol + '_' + kind)

    #deletes the entinre position from the memcache
    def delete_all(self):
        self.delete_blank('position')
        self.delete_blank('vols')
        self.delete_blank('past_dividends')
        self.delete_blank('projected_dividends')
        self.delete_blank('option_chain')


class GreeksMemcache:
    'this class handles the greeks in the memcache'

    #return the greeks of a single option description and None if not found
    def get_single(self, option_description):
        return memcache.get(option_description)

    #returns a dictionary of descriptions and the greeks associated with it
    #if not found the description is not entered into the dict
    def get_multi(self, option_description_list):
        return memcache.get_multi(option_description_list)

    #sets a single option in the memcache
    def set_single(self, option_description, option_greeks):
        memcache.set(option_description, option_greeks)

    #sets multiple description/greek pairs from a dict
    def set_multi(self, option_description_dict):
        memcache.set_multi(option_description_dict)

    #deletes a single description from the memcache
    def delete_single(self, option_description):
        memcache.delete(option_description)

    #deletes a list of desriptions from the memcahce
    def delete_multi(self, option_description_list):
        memcache.delete_multi(option_description_list)


