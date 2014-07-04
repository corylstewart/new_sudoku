import datetime
import time
import copy
import binomial_tree as bt
import hull

class OptionSymbol:
    '''this class creates an object containing the strike, expiration (datetime), days to expiration,
    whether it is a call or put, and the symbol of the option'''

    def __init__(self,optionsymbol):
        strike = str(int(optionsymbol[-8:]))
        self.strike_string = str(int(optionsymbol[-8:]))
        self.strike = float(self.strike_string)/1000
        self.year = int(optionsymbol[-15:-13])+2000
        self.month = int(optionsymbol[-13:-11])
        self.day = int(optionsymbol[-11:-9])
        self.exdatetime = datetime.datetime(self.year, self.month, self.day)
        if self.exdatetime.weekday() <> 5:      #if the option does not expire on a saturday bump it one day
            self.exdatetime = datetime.datetime(self.year, self.month, self.day+1)
        self.time = (self.exdatetime - datetime.datetime.today()).days / 365.0
        if self.time == 0:                      #if the option expires today add half a day to the expiration
            self.time = 0.5/362.0
        self.cp = optionsymbol[-9:-8]
        self.symbol = optionsymbol[0:-15]

class OptionPricer:
    '''this class calls the Binomial tree class if the stock does not pay a dividend
    and calls the Hull class if the stock does pay a dividend and return the greeks'''

    def __init__(self, strike, spot, vol, rate, time, div = []):
        if div == []:
            self.greeks = bt.BinomialTree(strike, spot, rate, vol, time)
        else:
            self.greeks = hull.Hull(strike, spot, rate, vol, time, div = div)

class Option:
    '''this class creates the desciption of a option based on the strike, spot,
    volatility, time to expiration, interest rate, and dividend if one is paid'''

    def __init__(self, optionsymbol, spot, vol, rate = .005, div = []):
        self.spot = spot
        self.vol = vol
        self.rate = rate
        self.div = div

        self.optionsymbol = OptionSymbol(optionsymbol)
        self.description = self.optionsymbol.strike_string + \
                            str(int(self.spot*1000)) + \
                            str(int(self.vol*100000)) + \
                            str(int(self.optionsymbol.time*365000)) + \
                            str(int(self.rate*100000))

        #if the stock pays a dividend prepend the description with todays date and stock symbol
        if len(self.div) <> 0:
            today = datetime.date.today()
            stock_symbol = optionsymbol[:-15]
            self.description = stock_symbol + str(today.year) + \
                    str(today.month) + str(today.day) + self.description

    #using the OptionPrice class create the greeks associated with this description
    def price(self):
        self.optionpricer = OptionPricer(self.optionsymbol.strike, self.spot, \
                        self.vol, self.rate, self.optionsymbol.time, div = self.div)


#for use while debugging
def print_all(o, keyin = ''):
    keylist = o.__dict__.keys()
    keylist.sort()
    for key in keylist:
        if type(o.__dict__[key]) == type(o):
            print_all(o.__dict__[key], keyin = keyin + str(key))
        else:
            print keyin,key,'=', o.__dict__[key]

