import time
import datetime
import copy
from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext.ndb import metadata

#from option_model import option_pricer as op

#create the option position class
class OptionPosition(ndb.Model):
    user = ndb.StringProperty()
    symbol = ndb.StringProperty()
    position = ndb.PickleProperty()
    past_dividends = ndb.PickleProperty()
    projected_dividends = ndb.PickleProperty()
    vols = ndb.PickleProperty()

    #query the DB for a position based on user and symbol
    def get_user_position(self, user, symbol):
        user_position = OptionPosition.query(OptionPosition.user == user, OptionPosition.symbol == symbol)
        if user_position.count() == 1:      #if one position is found return it
            for user_pos in user_position:
                return user_pos
        elif user_position.count() == 0:    #if no position is found return None
            return None
        else:
            for user_pos in user_position:  #if multiple positions are found delete them and return None
                user_pos.key.delete()
            return None

    #query the DB for all positions held by a user
    def get_user_book(self, user):
        user_book = []
        positions = OptionPosition.query(OptionPosition.user == user)
        for position in positions:
            user_book.append(position)
        return user_book

    #put a new postion in the DB based on user and symbol
    def put_user_position(self, user, symbol, position,\
                          past_dividends, projected_dividends, vols):
        self.delete_user_position(user, symbol)     #delete any old positions for that user/symbol
        user_position = OptionPosition(user = user, #add the new position for the user/symbol
                                       symbol = symbol,
                                       position = position,
                                       past_dividends = past_dividends,
                                       projected_dividends = projected_dividends,
                                       vols = vols)
        user_position.put()

    #remove a position based on the user and symbol
    def delete_user_position(self, user, symbol):
        positions = OptionPosition.query(OptionPosition.user == user, OptionPosition.symbol == symbol)
        for position in positions:
            position.key.delete()
                            

#create the option greeks class
class OptionGreeks(ndb.Model):
    option_description = ndb.StringProperty()   #the description of the option based on my symbology
    greeks = ndb.PickleProperty()               #the greeks associated with that position

    #return the greeks of a specific option desciprion
    def get_single_option_greeks(self, option_description):
        option_greeks_dict = {}
        option_greeks = OptionGreeks.query(OptionGreeks.option_description == option_description)
        if option_greeks.count() == 1:  #if one result is found return it
            for option in option_greeks:
                option_greeks_dict[option_description] = option.greeks
            return option_greeks_dict
        elif option_greeks.count() == 0: #if not results are found return an empty dict
            return {}
        else:
            for option in option_greeks:    #if multiple results are ofund delete them
                option.key.delete()         #and return an empty dict
            return {}

    #query multiple option desriptions and return a dict of dicts
    def get_multi_option_greeks(self, option_description_list):
        option_greeks_dict = {}     #create an empty dict to add the descriptions to
        for option_description in option_description_list:
            option_greeks = self.get_single_option_greeks(option_description)
            if len(option_greeks) == 1:     #if a result is returned add that description to the dict
                option_greeks_dict[option_description] = option_greeks[option_description]
        return option_greeks_dict
    
    #add a single description/greek to the DB
    def put_single_option_greeks(self, option_description, option_greeks):
        self.delete_single_greeks(option_description) #delete an old descriptions that match
        option = OptionGreeks(option_description = option_description,  #add the new desription/greek
                              greeks = option_greeks)
        option.put()
        
    #add multiple desciptions/greeks to the DB the input is a dict of descriptions/greeks
    def put_multi_option_greeks(self, option_greeks_dict):
        for option_description in option_greeks_dict:
            self.put_single_option_greeks(option_description, option_greeks_dict[option_description])

    #delete a single description
    def delete_single_greeks(self, option_description):
        option_greeks = OptionGreeks.query(OptionGreeks.option_description == option_description)
        for option in option_greeks:
            option.key.delete()

    #delete a number of descriptions, the input is a list of descriptions
    def delete_multiple_greeks(self, option_description_list):
        db_keys = []
        for option_description in option_description_list:
            greeks = OptionGreeks.query(OptionGreeks.option_description == option_description)
            for greek in greeks:
                db_keys.append(greek.key)
        ndb.delete_multi(db_keys)

    #deletes the 500 of descriptions from the DB
    def delete_all_greeks(self):
        greeks = OptionGreeks.query().fetch(limit = 500)
        for greek in greeks:
            greek.key.delete()