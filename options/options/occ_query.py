import csv
import urllib2
import string
import datetime
import json

#from google.appengine.api import memcache

class OccQuery:
    'this class queries the occ for optionable stocks and option chains for stocks'

    #query the occ for the list of optionable stocks
    def get_occ_listed_stocks(self):
        try:
            url = 'http://www.theocc.com/webapps/delo-download?prodType=EU&downloadFields=US&format=txt'
            r = urllib2.urlopen(url)
            words = r.readlines()
            optionable = []
            for word in words:
                optionable.append(word.split()[0])
            return optionable
        except:
            return None

    #query the OCC for the complete option chain
    '''def get_occ_csv_big_option_chain(self, stock_symbol):
        #goes to the occ and requests the entire option chain for a symbol
        #writes the chain to memcache for future use
        url = 'http://www.theocc.com/webapps/series-search?symbolType=U&symbol=' + stock_symbol
        try:
            r = urllib2.urlopen(url)
        except:
            return False
        chain = r.read()
        chain = chain.split()
        start = chain.index('Limit')+1
        option_chain = {}
        #iterate through the list of options and create a dictionary of the
        #different variables that describe an option
        for i in range(start,len(chain)):
            if chain[i] == stock_symbol:
                start_symbol = stock_symbol + chain[i+1][2:] + chain[i+2] + chain[i+3]
                end_symbol = '00000' + chain[i+4] + chain[i+5]
                while len(end_symbol) > 8:
                    end_symbol = end_symbol[1:]
                call_symbol = start_symbol + 'C' + end_symbol
                put_symbol = start_symbol + 'P' + end_symbol
                option_chain[call_symbol] = {}
                option_chain[put_symbol] = {}
                option_chain[call_symbol]['year'] = chain[i+1]
                option_chain[call_symbol]['month'] = chain[i+2]
                option_chain[call_symbol]['day'] = chain[i+3]
                option_chain[call_symbol]['strike_integer'] = chain[i+4]
                option_chain[call_symbol]['strike_dec'] = chain[i+5]
                option_chain[call_symbol]['strike'] = chain[i+4]+'.'+chain[i+5]
                option_chain[call_symbol]['c/p'] = chain[i+6]+chain[i+7]
                option_chain[call_symbol]['c_open'] = chain[i+8]
                option_chain[call_symbol]['p_open'] = chain[i+9]
                option_chain[call_symbol]['position_limit'] = chain[i+10]
                option_chain[call_symbol]['call_symbol'] = call_symbol
                option_chain[call_symbol]['put_symbol'] = put_symbol
                option_chain[put_symbol]['year'] = chain[i+1]
                option_chain[put_symbol]['month'] = chain[i+2]
                option_chain[put_symbol]['day'] = chain[i+3]
                option_chain[put_symbol]['strike_integer'] = chain[i+4]
                option_chain[put_symbol]['strike_dec'] = chain[i+5]
                option_chain[put_symbol]['strike'] = chain[i+4]+'.'+chain[i+5]
                option_chain[put_symbol]['c/p'] = chain[i+6]+chain[i+7]
                option_chain[put_symbol]['c_open'] = chain[i+8]
                option_chain[put_symbol]['p_open'] = chain[i+9]
                option_chain[put_symbol]['position_limit'] = chain[i+10]
                option_chain[put_symbol]['call_symbol'] = call_symbol
                option_chain[put_symbol]['put_symbol'] = put_symbol
                expiry = datetime.date(int(option_chain[call_symbol]['year']),\
                    int(option_chain[call_symbol]['month']),int(option_chain[call_symbol]['day']))
                day_of_week = expiry.weekday()
                #if the option does not expire on a saturday add a day to the expiration
                #this is a kind of wierd thing that the occ did when they introduced weekly
                #options and set the expiration day on the last trading day instead of the
                #following day
                if day_of_week <> 5:
                    expiry = datetime.date(int(option_chain[call_symbol]['year']),\
                             int(option_chain[call_symbol]['month']),int(option_chain[call_symbol]['day'])+1)
                option_chain[call_symbol]['expiry'] = expiry
                option_chain[put_symbol]['expiry'] = expiry
                if datetime.date.today() > expiry:
                    option_chain.pop(put_symbol)
                    option_chain.pop(call_symbol)
        return option_chain'''

    def get_occ_csv_small_option_chain(self, stock_symbol):
        #goes to the occ and requests the entire option chain for a symbol
        #writes the chain to memcache for future use
        url = 'http://www.theocc.com/webapps/series-search?symbolType=U&symbol=' + stock_symbol
        try:
            r = urllib2.urlopen(url)
        except:
            return False
        chain = r.read()
        chain = chain.split()
        start = chain.index('Limit')+1
        option_chain = {}
        #iterate through the list of options and create a dictionary of the
        #different variables that describe an option
        for i in range(start,len(chain)):
            if chain[i] == stock_symbol:
                start_symbol = stock_symbol + chain[i+1][2:] + chain[i+2] + chain[i+3]
                end_symbol = '00000' + chain[i+4] + chain[i+5]
                while len(end_symbol) > 8:
                    end_symbol = end_symbol[1:]
                call_symbol = start_symbol + 'C' + end_symbol   #create the call symbol for a month/strike combo
                put_symbol = start_symbol + 'P' + end_symbol    #create the put symbol for a month.strike combo
                year = int(call_symbol[-15:-13])+2000           #make the expiration year integer
                month = int(call_symbol[-13:-11])               #make the expiration month integer
                day = int(call_symbol[-11:-9])                  #make the expiration day integer
                expiry = datetime.date(year, month, day)        #make a datetime object for the expiration

                option_chain[call_symbol] = {}                                      #create an empty dict for the call symbol
                option_chain[call_symbol]['c_open'] = chain[i+8]                    #add call open interest to call dict
                option_chain[call_symbol]['p_open'] = chain[i+9]                    #add put open interest to call dict
                option_chain[call_symbol]['position_limit'] = chain[i+10]           #add position limit to the call dict
                option_chain[call_symbol]['call_symbol'] = call_symbol              #add call symbol to the call dict
                option_chain[call_symbol]['put_symbol'] = put_symbol                #add the put symbol to the call dict
                option_chain[call_symbol]['strike_int'] = str(int(call_symbol[-8:-3]))  #add the strike integer to the call dict
                option_chain[call_symbol]['strike_decimal'] = call_symbol[-3:]          #add the string decimal to the call dict
                option_chain[call_symbol]['expiry'] = expiry                            #add the datetime expiration to the call dict
                option_chain[call_symbol]['expiry_string'] = call_symbol[-15:-9]        #add the string expiration to the call dict
                option_chain[put_symbol] = {}                                           #all the same as above but for the put dict
                option_chain[put_symbol]['c_open'] = chain[i+8]
                option_chain[put_symbol]['p_open'] = chain[i+9]
                option_chain[put_symbol]['position_limit'] = chain[i+10]
                option_chain[put_symbol]['call_symbol'] = call_symbol
                option_chain[put_symbol]['put_symbol'] = put_symbol
                option_chain[put_symbol]['strike_int'] = option_chain[call_symbol]['strike_int']
                option_chain[put_symbol]['strike_decimal'] = option_chain[call_symbol]['strike_decimal']
                option_chain[put_symbol]['expiry'] = expiry
                option_chain[put_symbol]['expiry_string'] = option_chain[call_symbol]['expiry_string']
                '''if the option does not expire on a saturday add a day to the expiration
                this is a kind of wierd thing that the occ did when they introduced weekly
                options and set the expiration day on the last trading day instead of the
                following day'''
                day_of_week = option_chain[call_symbol]['expiry'].weekday() #saturday is represented as 5
                if day_of_week <> 5:                                        #so for all other days bump the date
                    option_chain[call_symbol]['expiry'] = datetime.date(year, month, day+1)
                    option_chain[put_symbol]['expiry'] = datetime.date(year, month, day+1)
                if datetime.date.today() >= expiry:     #remove any optiontions that have expired
                    option_chain.pop(call_symbol)       #really only mnatters on weekends because the occ
                    option_chain.pop(put_symbol)        #has not updated the file yet
        return option_chain

    #create a odered list of the options and return the list
    def create_ordered_list(self, option_chain):
        ordered_list = [key for key in option_chain if key[-9:-8] <> 'P']   #create a list of call symbols
        ordered_list.sort()         #sort the list, this sorts it by strike and by expiration
        today = datetime.date.today()
        rem = []                        #create empty list for options that need to be removed because the have expired
        for option in ordered_list:
            ex = option_chain[option]['expiry']
            if ex <= today:
                rem.append(option)
        for r in rem:                   #cycle through list of names to be removed
            try:
                ordered_list.remove(r)
            except:
                pass
        return ordered_list

    #create a list of expirations based on the option chain
    def create_expiry_list(self, option_chain, type):
        expiry = []     #create an empty list for new expirations that have not been found
        for option in option_chain:
            if option_chain[option][type] not in expiry:    #if the expiration is not in the list add it
                expiry.append(option_chain[option][type])
        expiry.sort()       #sort the list by expiration closest to furthest
        return expiry

#o = OccQuery()
#p = o.get_occ_csv_small_option_chain("FB")
