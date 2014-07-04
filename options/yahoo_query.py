import stockretriever as sr
import json
import urllib2
import time
import csv
import datetime

class YahooQuery:

    #print json so it is easier to read
    def pretty_print_json(self, json_obj):
        print json.dumps(json_obj, sort_keys=True, indent=4, separators=(',', ': '))

    #query yahoo for the current price of the stock
    def stock_px(self, stock_symbol):
        try:
            if type(stock_symbol) != type(list()):  #if the stock_symbol is not a list type
                stock_symbol = [stock_symbol]       #make a list containing the stock symbol
            stock = sr.StockRetriever()
            stock_info = stock.get_current_info(stock_symbol)   #get the stocks information from yahoo
            if stock_info["ErrorIndicationreturnedforsymbolchangedinvalid"] == 'null':  #if it is a bad symbol return
                return 'Invalid Symbol'                                                 #return invalid symbol
            return float(stock_info['LastTradePriceOnly'])                              #return the price of the stock
        except:
            return 'error'                                          #return error if unable to get a stock price from yahoo

    #query yahoo for the dividend hisory of a stock
    def get_dividend(self, stock_symbol):
        try:
            url = 'http://ichart.finance.yahoo.com/table.csv?s='
            url += stock_symbol
            url += '&a=01&b=19&c=2008&d=11&e=19&f=2016&g=v&ignore=.csv'     #request the dividends paid since 2008
            response = urllib2.urlopen(url)
            csvfile = csv.reader(response)
        except:
            return [], False                             #return an empty list and false which signifies an error
        dividends = []
        for row in csvfile:
            if row <> ['Date', 'Dividends']:
                day = row[0][8:10]
                month = row[0][5:7]
                year = row[0][:4]
                ex = month + '/' + day + '/' + year                         #create a string represntation of the ex-date
                ex_date = datetime.date(int(year), int(month), int(day))    #create a datetime object for the ex-date of the dividends
                dividends.append([ex, float(row[1]), ex_date])
        return dividends, True                                  #return a list of divideds and date and true which signinfies a successfull query

    #using past dividends create a projected dividend stream
    def create_div_projections(self, past_dividends):
        if past_dividends == 'Error':
            return 'Error'
        past_dates = past_dividends
        today = datetime.date.today()                                       #create a datetime object 
        year_ago = datetime.date(today.year -1, today.month, today.day)     #using the datetime create a datetime oject for one year ago
        years_worth = []                                                    #create empty list for one years worth of dividends
        upcoming = []                                                       #create empty list for the projhected dividend
        for dividend in past_dates:
            if dividend[2] < today and year_ago <= dividend[2]:             #for the div in past dates if they were within the last year
                years_worth.append(dividend)                                #append the years worth list
        years_worth.reverse()                                               #reverse sort the years worth list so that we can create the projections
        for i in range(1,5):
            for ex_date in years_worth:
                new_date_obj = datetime.date(ex_date[2].year+(i*1), ex_date[2].month, ex_date[2].day)       #using the old ex-dates create a future ex-date
                new_date_str = str(new_date_obj.month) + '/' + str(new_date_obj.day) + '/' + str(new_date_obj.year) #create a string reprsentation of the date
                upcoming.append([new_date_str, ex_date[1], new_date_obj])           #add the dividend to the upcoming list
        return upcoming