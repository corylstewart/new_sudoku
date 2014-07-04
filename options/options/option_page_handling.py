from SuperHandler import SuperHandler as SH
from options import memcache_and_db as mdb
from options import option_db as odb
from options import option_memcache as om
from options import option_greek_retriever as ogr
from options import yahoo_query as yq
from options import fix_format as ff
from options import price_rounding as pr
import time


class OptionPageHandler(SH.SuperHandler):
    def get(self):
        self.arg_dict['use_rounding'] = 'Checked'                           #render the blank template
        self.arg_dict['limited_strikes'] = 'Checked'
        self.render('option-chain.html', **self.arg_dict)

    def post(self):
        start_time = time.time()                                            #set a start time to evaluate efficiency

        stock_button = self.request.get('symbol_submit')                    #check whick buttons have been checked
        commit_button = self.request.get('commit_submit')
        database_write = self.request.get('database_write')
        precache = self.request.get('precache')
        use_rounding = self.request.get('use_rounding')
        limited_strikes = self.request.get('limited_strikes')

        if database_write:                                                  #set the values that the template will use
            self.arg_dict['database_write'] = 'Checked'                     #in the arg dict
            self.use_db = True
        else:
            self.arg_dict['database_write'] = False
            self.use_db = False
        if precache:
            self.arg_dict['precache'] = 'Checked'
            self.precache = True
        else:
            self.arg_dict['precache'] = False
            self.precache = False
        if use_rounding:
            self.arg_dict['use_rounding'] = 'Checked'
            self.use_rounding = True
        else:
            self.arg_dict['use_rounding'] = False
            self.use_rounding = False
        if limited_strikes:
            self.arg_dict['limited_strikes'] = 'Checked'
            self.limited_strikes = True
        else:
            self.arg_dict['limited_strikes'] = False
            self.limited_strikes = False

        self.arg_dict['error'] = ''                                         #set error to empty string
        self.error = False

        if self.user == None:                                               #if user is None set it to 'base'
            self.user = 'base'

        self.stock_symbol = self.request.get('stock_symbol')                #get stock symbol from 'stock_symbol'
        self.stock_symbol = self.stock_symbol.upper()                       #make the stock symbol uppercase
        self.arg_dict['stock_symbol'] = self.stock_symbol                   #add stock symbol to the arg_dict

        self.rate = self.request.get('interest_rate')                       #get the interest rate and if can't be
        try:                                                                #made a float set it to a generic value
            self.rate = float(self.rate)
        except:
            self.rate = .005
        self.arg_dict['rate'] = self.rate

        self.stock_step = .01                                               #set the stock step to .01 will be used if
                                                                            #precache is not used


        if stock_button:
            self.stock_button_clicked()                                     #if stock_button is selected call stock button

        if commit_button:
            self.commit_button_clicked()                                    #if commit button is selected call commit button

        if not self.error:                                                  #if there is an error skip calculations
            if use_rounding :
                self.stock_step = .05                                           #if use_rounding set precache steps to .05
                rounding = pr.PriceRounding()                                   #instantiate PriceRounding
                self.old_spot = self.spot                                       #set old_spot to the actual spot
                self.spot = rounding.round_stock_price(self.old_spot)           #set spot to rounded spot
                self.old_vols = self.arg_dict['vols']                           #set old_vols to the actual vols
                self.vols = rounding.round_vol_dict(self.old_vols)              #set vols to rouded vols

            self.calc_positions()                                               #calculate the greeks based on the inputs

            if use_rounding:
                self.fix_rounding()                                             #if rounding was used adjsut the greeks for offsets

        if self.user == 'base':
            self.user = None                                                #return the user to none   fix this at some point

        if precache:                                                        #if precache is selected precache the values
            self.precache_values()                                          #for differnt prices around spot

        self.arg_dict['ex_time'] = time.time() - start_time                 #set the end time for preformance evaluation
        self.render('option-chain.html', **self.arg_dict)                   #render the page



    def stock_button_clicked(self):  
        user_position = mdb.MdbPosition(self.user, self.stock_symbol, self.use_db)          #instantiate a MdbPosition

        self.stock_is_listed = user_position.stock_is_listed                                #make sure the stock is occ listed

        self.div_success = user_position.div_success                                        #make sure the dividend was sucessfully retieved
        if self.stock_is_listed == False:                                                   #if stock_is_listed of div_success are false set
            self.arg_dict['error'] = 'Sorry that is not an Optionable Symbol'               #self.error to true and create an error message
            self.error = True
            return
        if self.div_success == False:
            self.arg_dict['error'] = 'Sorry there was a problem getting the dividend try again in a minute'
            self.error = True
            return
        
        yahoo = yq.YahooQuery()
        self.spot = yahoo.stock_px(self.stock_symbol)                                       #get the stock price from Yahoo
        if self.spot == 'error' or self.spot == 'Invalid Symbol':                           #if there is an error set self.error to true
            self.arg_dict['error'] = 'Sorry there was a problem getting the stock price try again in a minute'      #create error message
            self.error = True
            return
        self.arg_dict['stock_price'] = format(self.spot, '.2f')                             #format stock price to hundreths place
        self.arg_dict['option_chain'] = user_position.option_chain                          #set the rest of the template values
        self.option_chain = user_position.option_chain                                      #and the object values
        self.arg_dict['ordered_list'] = user_position.ordered_list
        self.ordered_list = user_position.ordered_list
        self.arg_dict['expiry'] = user_position.expiry
        self.arg_dict['expiry_string'] = user_position.expiry_string
        self.arg_dict['position'] = user_position.position
        self.arg_dict['expiration_vols'] = user_position.expiration_vols
        self.arg_dict['past_dividends'] = user_position.past_dividends
        self.arg_dict['projected_dividends'] = user_position.projected_dividends
        self.arg_dict['model_dividend'] = user_position.model_dividend
        self.dividend = user_position.model_dividend
        self.arg_dict['vols'] = user_position.vols
        self.vols = user_position.vols

    def commit_button_clicked(self):
        self.stock_symbol = self.request.get('stock_symbol_hidden')                         #get the stock name from the hidden input
        self.stock_symbol = self.stock_symbol.upper()                                       #keeps the user from changing the stock name
        self.arg_dict['stock_symbol'] = self.stock_symbol

        user_position = mdb.MdbPosition(self.user, self.stock_symbol, self.use_db)          #instantiate a MdbPosition

        self.stock_is_listed = user_position.stock_is_listed                                #kind of feel this is repetitive
        self.div_success = user_position.div_success                                        #but would rather keep this stuff seperate
        if self.stock_is_listed == False:                                                   #do need to refactor this though
            self.arg_dict['error'] = 'Sorry that is not an Optionable Symbol'
            self.error = True
            return
        if self.div_success == False:
            self.arg_dict['error'] = 'Sorry that was a problem getting the dividend try again in a minute'
            self.error = True
            return

        self.spot = self.request.get('stock_price')                                         #if the stock price user entered is not valid
        try:
            self.spot = float(self.spot)                                                    #query yahoo for a valid spot value
            self.arg_dict['stock_price'] = format(self.spot, '.2f')
        except:                                                                             #if yahoo does not return a value
            yahoo = yq.YahooQuery()                                                         #set self.error to true
            self.spot = yahoo.stock_px(self.stock_symbol)
            if self.spot == 'error' or self.spot == 'Invalid Symbol':
                self.arg_dict['error'] = 'Sorry there was a problem getting the stock price try again in a minute'
                self.error = True
                return
            self.arg_dict['stock_price'] = format(self.spot, '.2f')


        self.arg_dict['option_chain'] = user_position.option_chain                          #set the template values and the
        self.option_chain = user_position.option_chain                                      #object values for use later
        self.arg_dict['ordered_list'] = user_position.ordered_list
        self.ordered_list = user_position.ordered_list
        self.arg_dict['expiry'] = user_position.expiry
        self.arg_dict['expiry_string'] = user_position.expiry_string
        self.arg_dict['position'] = user_position.position
        self.arg_dict['expiration_vols'] = user_position.expiration_vols
        self.arg_dict['past_dividends'] = user_position.past_dividends
        self.arg_dict['projected_dividends'] = user_position.projected_dividends
        self.arg_dict['model_dividend'] = user_position.model_dividend
        self.dividend = user_position.model_dividend
        self.arg_dict['vols'] = user_position.vols
        self.vols = user_position.vols

        self.get_user_vols()                                                                #get the users vols that they entered
        self.get_user_position()                                                            #get the users position that they entered

        self.reset_position = False                                                         #set a validation point
        self.compare_positions_and_vols()                                                   #check if the vols of position has changed
        if self.reset_position:                                                             #if so set the new position and vols in the DB
            user_position = mdb.MdbPosition(self.user, self.stock_symbol, self.use_db)
            self.arg_dict['vols'] = user_position.vols

    #get the users inputs for new vol, skew and smile
    def get_user_vols(self):
        new_user_vols = {}
        for exp in self.arg_dict['expiry_string']:                                          #for expiration in expiry string
            try:
                new_user_vols[exp] = {}                                                     #get the users input from the webpage
                new_user_vols[exp]['vol'] = float(self.request.get('spot_vol_'+ exp))       #if any of the values can't be made a
                new_user_vols[exp]['skew'] = float(self.request.get('skew_'+ exp))          #float set the value to None
                new_user_vols[exp]['smile'] = float(self.request.get('smile_'+ exp))
            except:
                new_user_vols = None
        self.arg_dict['new_user_vols'] = new_user_vols

    #get the users inputs for new positions
    def get_user_position(self):
        new_user_position = {}                                                              #create the empty dict
        for option in self.arg_dict['option_chain']:
            try:
                new_user_position[option] = int(self.request.get(option+'_position'))       #get the new user position for the line
            except:
                new_user_position[option] = self.arg_dict['position'][option]               #if not found set it to the old position value
        try:
            new_user_position['stock'] = int(self.request.get('stock_position'))            #check if the value is an integer
        except:
            new_user_position['stock'] = self.agr_dict['position']['stock']                 #if not set it to the old position value
        self.arg_dict['new_user_position'] = new_user_position

    #compare the old position versus the new postition
    def compare_positions_and_vols(self):
        push_to_db = False                                                                  #set push to DB as False so that if no changes are made the DB is not hit
        if self.arg_dict['position'] <> self.arg_dict['new_user_position']:                 #if positions do not match
            self.arg_dict['position'] = self.arg_dict['new_user_position']                  #set position to the new position
            put_position = om.PositionMemcache(self.user, self.stock_symbol)                #put position into memcache
            put_position.set_position(self.arg_dict['position'])                            
            push_to_db = True                                                               #set push to DB as True
        if self.arg_dict['expiration_vols'] <> self.arg_dict['new_user_vols']:              #if the vols do not match
            if self.arg_dict['new_user_vols'] <> None:                                      #if there was no error in getting the user vols
                self.arg_dict['expiration_vols'] = self.arg_dict['new_user_vols']           #set the vols to the user vols
                put_vol = om.PositionMemcache(self.user, self.stock_symbol)                 #set the vols into memcache
                put_vol.set_vols(self.arg_dict['expiration_vols'])
                push_to_db = True
                self.reset_position = True
            if push_to_db == True:                                                          #if any chages were made set the changes to the DB
                new_pos = odb.OptionPosition()
                new_pos.put_user_position(self.user,
                                          self.stock_symbol,
                                          self.arg_dict['position'],
                                          self.arg_dict['past_dividends'],
                                          self.arg_dict['projected_dividends'],
                                          self.arg_dict['expiration_vols'])




    def calc_positions(self):
        option_greeks = ogr.MakeAllGreeks(self.spot, self.ordered_list, self.option_chain,          #calculate the values of all of the options
                                          self.vols, self.rate, self.dividend,                      #in the option chain
                                          self.use_db, self.use_rounding)


        self.arg_dict['greeks'] = option_greeks.greeks                                              #set the arg_dict to the calculated values

        pos_total = mdb.PositionTotals()
        self.arg_dict['expiration_totals'] = pos_total.calculate_expiration_totals(self.arg_dict['greeks'], #calculate the monthly greek totals
                                            self.arg_dict['position'], self.arg_dict['expiry_string'],
                                            self.arg_dict['option_chain'], self.arg_dict['ordered_list'])
        self.arg_dict['position_totals'] = pos_total.position_total(self.arg_dict['expiration_totals'],     #calculate the total position greeks
                                                                    self.arg_dict['position'])

        self.arg_dict['show_list'] = self.arg_dict['ordered_list']                                          #create a new list based on ordered list
                                                                                          

        fix_format = ff.FixFormat()                                                                         #fix the format so that only a few deciaml
        self.arg_dict['formatted_greeks'] = fix_format.fix_greeks_format(self.arg_dict['greeks'])           #places are show
        self.arg_dict['formatted_expiration_totals'] = fix_format.fix_expiration_totals_format(self.arg_dict['expiration_totals'])
        self.arg_dict['formatted_position_totals'] = fix_format.fix_postition_totals_format(self.arg_dict['position_totals'])

        if self.limited_strikes:                                                                            #if linited strikes is selected
            remove = []                                                                                     #remove strikes with a call delta
            for option in self.arg_dict['ordered_list']:                                                    #lower than .25 and higher than .75
                if self.arg_dict['greeks'][option]['call']['delta'] > .75 or self.arg_dict['greeks'][option]['call']['delta'] < .25:
                        remove.append(option)
            for option in remove:
                self.arg_dict['ordered_list'].remove(option)

    def fix_rounding(self):                                                                                 #if option prices were rounded
            rounding = pr.PriceRounding()                                                                   #adjust the price of the call and the
            for option in self.arg_dict['greeks']:                                                          #put based upon difference in stock price
                self.arg_dict['greeks'][option]['call']['value'] = \
                    rounding.adjust_price_for_stock_price_and_vol(self.spot, self.old_spot,                 #and the diffence in volatility
                                                                  self.arg_dict['greeks'][option]['call']['delta'], 
                                                                  self.old_vols[option], self.old_vols[option],
                                                                  self.arg_dict['greeks'][option]['call']['vega'],
                                                                  self.arg_dict['greeks'][option]['call']['value'])
                self.arg_dict['greeks'][option]['put']['value'] = \
                    rounding.adjust_price_for_stock_price_and_vol(self.old_spot, self.spot, 
                                                                  self.arg_dict['greeks'][option]['put']['delta'], 
                                                                  self.old_vols[option], self.old_vols[option],
                                                                  self.arg_dict['greeks'][option]['put']['vega'],
                                                                  self.arg_dict['greeks'][option]['put']['value'])
            fix_format = ff.FixFormat()
            self.arg_dict['formatted_greeks'] = fix_format.fix_greeks_format(self.arg_dict['greeks'])       #fix the format of the values
            self.arg_dict['formatted_expiration_totals'] = fix_format.fix_expiration_totals_format(self.arg_dict['expiration_totals'])
            self.arg_dict['formatted_position_totals'] = fix_format.fix_postition_totals_format(self.arg_dict['position_totals'])

    def precache_values(self):                                                                              #if precache is selected
        self.save_spot = self.spot                                                                          #create a range of stock prices
        self.spot_steps = [round(self.spot + self.stock_step * x,2) for x in xrange(-3,4) if x <> 0]        #so that values can be calculated
        for spot in self.spot_steps:                                                                        #for furure user
            self.spot = spot
            self.calc_positions()
        self.spot = self.save_spot                                                                          #set spot back to original spot price



class DeleteOptions(SH.SuperHandler):                                                                       #this is just for clearing out old values in
    def get(self):                                                                                          #in the database
        if self.check_admin():
            self.render('option-db.html', **self.arg_dict)

    def post(self):
        if self.check_admin():
            btn = self.request.get('delete_db_btn')
            if btn:
                options = odb.OptionGreeks()
                options.delete_all_greeks()
                self.write('done')
