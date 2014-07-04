from options import option_memcache as om
from options import option_db as odb
from options import occ_query as occ
from options import make_blanks as mb
from options import yahoo_query as yq
from options import reconcile as rec
from options import vol_skew as vs
from options import model_dividend as md
import datetime

class MdbPosition:
    'this class handles the reading and writing positions to both the database and memcache'

    #initialize all of the variable that are going to be used in the position
    def __init__(self, user = 'base', stock_symbol = '', use_db = False):
        self.user = user
        self.stock_symbol = stock_symbol
        self.use_db = use_db
        self.push_to_db = False
        self.stock_is_listed = self.is_listed()
        self.option_chain = ''
        self.ordered_list = ''
        self.expiry = ''
        self.expiry_string = ''
        self.position = ''
        self.expiration_vols = ''
        self.past_dividends = ''
        self.projected_dividends = ''
        self.div_success = True
        self.vols = ''
        self.model_dividend = ''


        if self.stock_is_listed:
            self.option_chain = self.get_option_chain()
            self.ordered_list = self.get_odered_list()
            self.expiry = self.get_expiry_list('expiry')
            self.expiry_string = self.get_expiry_list('expiry_string')
            self.position = self.get_position()
            self.expiration_vols = self.get_expiration_vols()
            self.past_dividends = self.get_past_dividends()
            self.projected_dividends = self.get_projected_dividends()

            self.check_memcache_returns()
            self.reconcile_position()
            self.reconcile_expiration_vols()

            vols = vs.VolSkew()
            self.vols = vols.make_vol_skew(self.expiration_vols, self.option_chain)
            self.model_dividend = md.ModelDividend().make_model_dividend(self.projected_dividends)

    #check to see if the stock is an optionable one
    def is_listed(self):
        occ_list = om.PositionMemcache(self.user, self.stock_symbol)    #query memcache for the occ_list
        occ_listed_stocks = occ_list.get_occ_listed_stocks()
        if occ_listed_stocks == None:                                   #if occ_list was not in the memcache
            make_occ = occ.OccQuery()                                   #query the occ for the occ list
            occ_listed_stocks = make_occ.get_occ_listed_stocks()
            occ_list.set_occ_listed_stocks(occ_listed_stocks)           #set the occ list in the memcahce
        if self.stock_symbol in occ_listed_stocks:                      #check to see if the stock is listed in the occ list
            return True
        else:
            return False

    #get the option chain
    def get_option_chain(self):
        opt_chain = om.PositionMemcache(self.user, self.stock_symbol)   #check to see if the chain is in the memcache
        option_chain = opt_chain.get_option_chain()
        if option_chain == None:                                        #if not query the occ for the option chain
            make_occ = occ.OccQuery()
            option_chain = make_occ.get_occ_csv_small_option_chain(self.stock_symbol)
            opt_chain.set_option_chain(option_chain)
        return option_chain

    #get the ordered list
    def get_odered_list(self):
        ord_list = occ.OccQuery()                                       #create a OccQuery object
        ordered_list = ord_list.create_ordered_list(self.option_chain)  #create the ordered list using the option chain
        return ordered_list

    #get the expiry list
    def get_expiry_list(self, type):
        exp_list = occ.OccQuery()                                       #create a OccQuery object
        expiry = exp_list.create_expiry_list(self.option_chain, type)   #create the expiry datetime list using the option chain
        return expiry
    
    #create the expiry string list
    def make_expiry_string(self):
        expiry_string = []
        exp_list = occ.OccQuery()                                       #create a OccQuery object
        for exp in self.expiry:                                         #iterate over the expiry list
            expiry_string.append(exp_list.create_expiry_string(exp))    #convert the datetime type to a date string
        return expiry_string

    #get the position from the memcache
    def get_position(self):
        user_pos_mem = om.PositionMemcache(self.user, self.stock_symbol)
        return user_pos_mem.get_position()

    #get the expiration vols from the memcache
    def get_expiration_vols(self):
        user_pos_mem = om.PositionMemcache(self.user, self.stock_symbol)
        return user_pos_mem.get_vols()

    #create the expiration vols string based on the expiration vols
    def make_expiration_vols_string(self):
        expiration_vols_string = {}
        convert_date = occ.OccQuery()                                       #create a OccQuery object
        for exp in self.expiration_vols:                                    #iterate over the expiry list
            vol_s = convert_date.create_expiry_string(exp)                  #convert the datetime type to a date string
            expiration_vols_string[vol_s] = self.expiration_vols[exp]       #add the vol/date to the dictionary
        return expiration_vols_string

    #get the past dividends from the memcache
    def get_past_dividends(self):
        user_pos_mem = om.PositionMemcache(self.user, self.stock_symbol)
        return user_pos_mem.get_past_dividends()

    #get the projected dividends from the memcache
    def get_projected_dividends(self):
        user_pos_mem = om.PositionMemcache(self.user, self.stock_symbol)
        return user_pos_mem.get_projected_dividends()

    #check to see is the memcache contained all the information about the user/symbol
    #if not query the database for that information
    def check_memcache_returns(self):
        #if any of the required fields are empty create a OptionPostion instance
        if self.position == None or self.past_dividends == None or self.projected_dividends == None or self.expiration_vols == None:
            user_pos_db = odb.OptionPosition()
            user_position = user_pos_db.get_user_position(self.user, self.stock_symbol)     #query the database for the user/symbol
            if user_position == None:                                                       #is user/symbol not found in the DB
                self.make_new_position()                                                    #create a new position
                new_pos = odb.OptionPosition()                                              #create a new OptionPosition instance
                if self.div_success:                                                        #if the dividend was found without an error
                    new_pos.put_user_position(self.user,                                    #put the new position in the database
                                              self.stock_symbol, 
                                              self.position, 
                                              self.past_dividends, 
                                              self.projected_dividends, 
                                              self.expiration_vols)
                else:                                                                       #if the dividend had an error
                    new_pos.put_user_position(self.user,                                    #put the new position in the database
                                              self.stock_symbol,                            #but note that there is a problem with
                                              self.position,                                #with the dividned
                                              'Error',
                                              'Error',
                                              self.expiration_vols)
                    self.div_success = False
            else:                                                                       #if the position was found in the database
                self.position = user_position.position                                  #set all of the variables to the MdbPosition instance
                self.expiration_vols = user_position.vols
                self.past_dividends = user_position.past_dividends
                self.projected_dividends = user_position.projected_dividends
                if self.past_dividends == 'Error':                                      #if there was an error previously on the dividend
                    new_divs = yq.YahooQuery()                                          #query yahoo for the dividned again
                    self.past_dividends, self.div_success = new_divs.get_dividend(self.stock_symbol)
                    self.projected_dividends = new_divs.create_div_projections(self.past_dividends)
                    if self.div_success:                                                #if the dividend was found
                        new_pos = odb.OptionPosition()                                  #place the position back in the database
                        new_pos.put_user_position(self.user,                            #with the correct dividned
                                                    self.stock_symbol, 
                                                    self.position, 
                                                    self.past_dividends, 
                                                    self.projected_dividends, 
                                                    self.expiration_vols)
            user_pos_mem = om.PositionMemcache(self.user, self.stock_symbol)            #instantiate PositionMemcache
            user_pos_mem.set_position(self.position)                                    #place the new position into the memcache
            user_pos_mem.set_past_dividends(self.past_dividends)
            user_pos_mem.set_projected_divideds(self.projected_dividends)
            user_pos_mem.set_vols(self.expiration_vols)

    #create a new position
    def make_new_position(self):
        make_blank = mb.MakeBlanks()                                                    #create a MakeBalnks instanvce
        self.position = make_blank.make_blank_position(self.option_chain)               #create a new empty position
        self.expiration_vols = make_blank.make_blank_vols(self.expiry_string)           #create a new generic exiration vols
        yahoo = yq.YahooQuery()                                                         #instatiate a YahooQuery
        self.past_dividends, self.div_success = yahoo.get_dividend(self.stock_symbol)   #get the past dividends from Yahoo
        self.projected_dividends = yahoo.create_div_projections(self.past_dividends)    #create the projected dividends

    #reconcile the position against the option chain
    def reconcile_position(self):
        old_position = self.position            #set a starting point to compare to later
        reconcile = rec.Reconcile()             #reconcile the position
        self.position = reconcile.reconcile_position(self.option_chain, self.position)
        if old_position <> self.position:       #if the new position and old position do not match
            mem = om.PositionMemcache(self.user, self.stock_symbol)
            mem.set_position(self.position)                         #set the new position in memcache
            db = odb.OptionPosition()                               #put the new position in the db
            db.put_user_position(self.user,
                                 self.stock_symbol,
                                 self.position,
                                 self.past_dividends,
                                 self.projected_dividends,
                                 self.expration_vols)

    #reconcile the expiration vols
    def reconcile_expiration_vols(self):
        old_vols = self.expiration_vols         #set a starting point to compare to later
        reconcile = rec.Reconcile()             #reconcile the vols
        self.expiration_vols = reconcile.reconcile_vols(self.expiration_vols, self.expiry_string)
        if old_vols <> self.expiration_vols:    #if the new vols and old vols do not match
            mem = om.PositionMemcache(self.user, self.stock_symbol)
            mem.set_vols(self.expiration_vols)                      #set the new vols in memcache
            db.put_user_position(self.user,                         #put the new vols in the db
                                 self.stock_symbol,
                                 self.position,
                                 self.past_dividends,
                                 self.projected_dividends,
                                 self.expiration_vols)


class MdbGreeks:
    'this class handles the reading and writing positions to both the database and memcache'

    #get a single greek
    def get_single_greek(self, option_description, use_db = False):
        mem = om.GreeksMemcache()
        mem_greek = mem.get_single(option_description)              #get a desciption from memcache
        if mem_greek <> None:                                       #if found return the value
            return mem_greeks
        elif use_db == True:                                        #if database read and write is True
            db = odb.OptionGreeks()                                 #query the database
            db_greek_dict = db.get_single_option_greeks(option_description)
            if db_greek_dict <> {}:                                 #if found in the database
                for description in db_greek_dict:
                    mem_greek = db_greek_dict[description]          #set the greeks in memcache
                    mem.set_single(description, mem_greek)          #return value of greeks
                    return mem_greek
            else:
                return {}                                           #if no values found return empty dict
        else:
            return {}

    #get multiple greeks
    def get_multi_greeks(self, option_description_list, use_db = False):
        mem = om.GreeksMemcache()
        mem_greeks = mem.get_multi(option_description_list)         #get multiple values from the memcache
        if use_db == True:                                          #if database read write is true
            for description in mem_greeks:                          #for the greeks found in the memcache
               option_description_list.remove(description)          #pop the found greeks off the list we are still looking for
            db = odb.OptionGreeks()
            db_greeks = db.get_multi_option_greeks(option_description_list) #query the DB for the remaining descriptions
            if len(db_greeks) > 0:
                mem.set_multi(db_greeks)                                    #for the greeks found in the DB write the values to memcache
            for description in db_greeks:
                mem_greeks[description] = db_greeks[description]            #add the greeks found in the DB to the dictionary that will be returned
        return mem_greeks

    #set a single greek
    def set_single_greek(self, description, greeks, use_db = False):
        greeks_mem = om.GreeksMemcache()
        greeks_mem.set_single(description,greeks)                           #set a single greek to memcache
        if use_db:                                                          #if DB read write is True
            greeks_db = odb.OptionGreeks()
            greeks_db.put_single_option_greeks(description, greeks)         #put the greeks into the DB

    #set multiple greeks
    def set_multi_greeks(self, greeks_dict, use_db = False):
        greeks_mem = om.GreeksMemcache()
        greeks_mem.set_multi(greeks_dict)                                   #set multiple greeks to memcache
        if use_db == True:                                                  #if DB read write is True
            greeks_db = odb.OptionGreeks()
            greeks_db.put_multi_option_greeks(greeks_dict)                  #put multiple greeks in the DB

class PositionTotals:
    'this class creates monthly and total greeks for the position'

    def calculate_expiration_totals(self,greeks, position, expiry_string, option_chain, ordered_list):
        expiration_totals = {}
        for exp in expiry_string:                                   #for every expiration in the expiry_string
            expiration_totals[exp] = {}                             #initialize the variables to 0
            expiration_totals[exp]['delta'] = 0
            expiration_totals[exp]['theta'] = 0
            expiration_totals[exp]['gamma'] = 0
            expiration_totals[exp]['vega'] = 0
        for option in ordered_list:                                 #for every option in the order list
            call_symbol = option_chain[option]['call_symbol']
            put_symbol = option_chain[option]['put_symbol']
            call_position = position[call_symbol]                   #get the position for the calls
            put_position = position[put_symbol]                     #get the position for the puts
            exp = option_chain[option]['expiry_string']
            expiration_totals[exp]['delta'] += call_position * greeks[option]['call']['delta'] * 100    #add to the totals of the greeks
            expiration_totals[exp]['delta'] += put_position * greeks[option]['put']['delta'] * 100      #for its repective expiration
            expiration_totals[exp]['theta'] += call_position * greeks[option]['call']['theta'] * 100
            expiration_totals[exp]['theta'] += put_position * greeks[option]['put']['theta'] * 100
            expiration_totals[exp]['gamma'] += call_position * greeks[option]['call']['gamma'] * 100
            expiration_totals[exp]['gamma'] += put_position * greeks[option]['put']['gamma'] * 100
            expiration_totals[exp]['vega'] += call_position * greeks[option]['call']['vega'] * 100
            expiration_totals[exp]['vega'] += put_position * greeks[option]['put']['vega'] * 100           
        return expiration_totals

    #using the monthly totals create a position total
    def position_total(self, expiration_totals, position):
        position_total = {}                 #inititalize the variable to 0
        position_total['delta'] = 0
        position_total['theta'] = 0
        position_total['gamma'] = 0
        position_total['vega'] = 0
        for exp in expiration_totals:       #for each expiration in the expiration totals
            position_total['delta'] += expiration_totals[exp]['delta']      #sum the totals up
            position_total['theta'] += expiration_totals[exp]['theta']      #for each of the greeks
            position_total['gamma'] += expiration_totals[exp]['gamma']
            position_total['vega'] += expiration_totals[exp]['vega']
        position_total['delta'] += position['stock']                        #adjust the delta for the amount of stock held
        return position_total



