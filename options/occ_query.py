import urllib2
import datetime
import copy

class OccOptionableList:

    def __init__(self):
        self.optionable_list = None
        self.retieved = None
        self._get_occ_listed_stocks()

    #query the occ for the list of optionable stocks
    def _get_occ_listed_stocks(self):
        try:
            url = 'http://www.theocc.com/webapps/delo-download?prodType=EU&downloadFields=US&format=txt'
            r = urllib2.urlopen(url)
            words = r.readlines()
            optionable = []
            for word in words:
                optionable.append(word.split()[0])
            self.optionable_list = optionable
            self.retieved = datetime.date.today()
        except:
            self.optionable_list = None
        return self.optionable_list

class OccOptionChain:
    def __init__(self, stock_symbol):
        self.stock_symbol = stock_symbol.upper()
        self.trades_on = None
        self.option_chain = None
        self.ordered_option_symbol_list = None       
        self.ordered_expirations_list = None
        self.ordered_expirations_string = None

        self._make_option_chain()
        self._create_ordered_expirations_list()
        self._create_ordered_option_symbol_list()
        self._create_ordered_expirations_string_list()

    def _make_option_chain(self):
        stock_symbol = self.stock_symbol
        url = 'http://www.theocc.com/webapps/series-search?symbolType=U&symbol=' + stock_symbol
        try:
            data = urllib2.urlopen(url)
        except:
            return False
        self.option_chain = {}
        data.readline()#clear: Series Search Results for
        data.readline()#clear: blank line
        data.readline()#clear: Products for this underlying symbol are traded on
        self.trades_on = data.readline().split()
        data.readline()#clear: blank line
        data.readline()#clear: Series/contract Strike Open Interest
        data.readline()#clear: ProductSymbol year Month Day Integer Dec C/P Call Put Position Limit	
        for line in data.readlines():
            option_list = line.split()
            if option_list[0] == stock_symbol and len(option_list) == 11:
                while len(option_list[4]) < 5:
                    option_list[4] = '0'+ option_list[4]
                symbol = option_list[0]
                year = option_list[1]
                year_short = year[-2:]
                month = option_list[2]
                day = option_list[3]
                strike_int = option_list[4]
                strike_dec = option_list[5]
                call_open = option_list[8]
                put_open = option_list[9]
                position_limit = option_list[10]
                start_sym = symbol + year_short + month + day
                end_sym = strike_int + strike_dec
                call_symbol =  start_sym + 'C' + end_sym
                put_symbol = start_sym + 'P' + end_sym
                ex_date_date = datetime.date(int(year), int(month), int(day))
                strike_price_str = strike_int + '.' + strike_dec
                while strike_price_str[0] == '0':
                    strike_price_str = strike_price_str[1:]
                if ex_date_date.weekday() <> 5:
                    try:
                        ex_date_date = datetime.date(int(year), int(month), int(day)+1)
                    except:
                        if month == '12' and day == '31':
                            ex_date_date = datetime.date(int(year) + 1, 1, 1)
                        else:
                            ex_date_date = datetime.date(int(year), int(month) + 1, 1)
                this_symbol = {'stock_symbol' : symbol,
                               'exp_year' : year,
                               'exp_year_short' : year_short,
                               'exp_month' : month,
                               'exp_day' : day,
                               'exp_datetime.date' : ex_date_date,
                               'strike_price' : float(strike_price_str),
                               'strike_price_str' : strike_price_str,
                               'strike_int' : strike_int,
                               'strike_dec' : strike_dec,
                               'position_limit' : position_limit,
                               'exp_date_str' : str(ex_date_date.month) + '/' + 
                                                str(ex_date_date.day) + '/' + 
                                                str(ex_date_date.year)
                               }
                self.option_chain[call_symbol] = copy.deepcopy(this_symbol)
                self.option_chain[call_symbol]['CP'] = 'C'
                self.option_chain[call_symbol]['open_interest'] = call_open
                self.option_chain[put_symbol] = copy.deepcopy(this_symbol)
                self.option_chain[put_symbol]['CP'] = 'P'
                self.option_chain[put_symbol]['open_interest'] = put_open


    #create a odered list of the options and return the list
    def _create_ordered_option_symbol_list(self):
        if not self.option_chain:
            return
        self.ordered_option_symbol_list = [key for key,value \
                         in self.option_chain.items() if 'P' not in key \
                         and value['exp_datetime.date'] > datetime.date.today()]
        self.ordered_option_symbol_list.sort()

    #create a list of expirations based on the option chain
    def _create_ordered_expirations_list(self):
        if not self.option_chain:
            return
        self.ordered_expirations_list = []
        for key, value in self.option_chain.items():
            if value['exp_datetime.date'] not in self.ordered_expirations_list:
                self.ordered_expirations_list.append(value['exp_datetime.date'])
        self.ordered_expirations_list.sort()

    def _create_ordered_expirations_string_list(self):
        self.ordered_expirations_string = []
        for exp in self.ordered_expirations_list:
            date = str(exp.month) + '/' + str(exp.day) + '/' + str(exp.year)
            self.ordered_expirations_string.append(date)