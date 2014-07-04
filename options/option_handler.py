from EnhancedHandler import EnhancedHandler as EH
import position_retriever as PR
import option_db as ODB
import time
import json
import copy
import datetime

class MakeArgDictPosition:
    def __init__(self, arg_dict, position):
        arg_dict['position'] = position.position
        arg_dict['option_chain'] = position.option_chain.option_chain
        arg_dict['trades_on'] = position.option_chain.trades_on
        arg_dict['stock_price'] = position.stock_price
        arg_dict['past_dividends'] = position.past_dividends
        arg_dict['projected_dividends'] = position.projected_dividends
        arg_dict['vols'] = position.vols
        arg_dict['ordered_option_symbol_list'] = position.option_chain.ordered_option_symbol_list
        arg_dict['ordered_expiration_datetime'] = position.option_chain.ordered_expirations_list
        arg_dict['ordered_expiration_string'] = position.option_chain.ordered_expirations_string
        arg_dict['interest_rate'] = position.rate

        new_option_chain = copy.deepcopy(position.option_chain.option_chain)
        for option,value in new_option_chain.items():
            if 'exp_datetime.date'in value:
                value['js_date_str'] = str(value['exp_datetime.date'].year) + \
                    '-' + str(value['exp_datetime.date'].month) + '-' + str(value['exp_datetime.date'].day)
                del value['exp_datetime.date']
               
        arg_dict['json_option_chain'] = json.dumps(new_option_chain)
        arg_dict['json_trades_on'] = json.dumps(position.option_chain.trades_on)
        arg_dict['json_vols'] = json.dumps(position.vols_str)
        arg_dict['json_trades_on'] = json.dumps(position.option_chain.trades_on)
        arg_dict['json_position'] = json.dumps(position.position)
        new_projected_dividends = copy.deepcopy(position.projected_dividends)
        for dividend in new_projected_dividends:
            dividend.pop()
        arg_dict['json_projected_dividends'] = json.dumps(new_projected_dividends)
        arg_dict['json_ordered_option_symbol_list'] = json.dumps(position.option_chain.ordered_option_symbol_list)
        arg_dict['json_ordered_expiration_string'] = json.dumps(position.option_chain.ordered_expirations_string)

class SavePosition:
    def __init__(self, page):
        self.stock_price = None
        self.stock_symbol = None
        self.option_chain = None
        self.vols = None
        self.position = None
        self.rate = None
        self.projected_dividends = None
        self.default_interest_rate = None
        self.trades_on = None
        self.ordered_expiration_datetime = None
        self.ordered_option_symbol_list = None
        self.ordered_expiration_string = None



        stock_symbol_hidden = page.request.get('stock_symbol_hidden')
        if not stock_symbol_hidden:
            page.arg_dict['error'] = "Can't save an empty position please load a stock first!"
        else:
            self.stock_symbol = stock_symbol_hidden
            page.arg_dict['stock_symbol'] = self.stock_symbol
            try:
                self.stock_price = float(page.request.get('stock_price'))
            except:
                self.stock_price = float(page.request.get('stock_price_hidden'))
            page.arg_dict['stock_price'] = self.stock_price

            try:
                self.rate = float(page.request.get('interest_rate'))
            except:
                self.rate = self.default_interest_rate
            page.arg_dict['interest_rate'] = self.rate

            self.get_json_object_from_page(page)
            self.make_non_json_objects(page)
            self.make_option_symbol_list(page)
            self.get_postion_from_page(page)
            self.get_vols_from_page(page)

            db = ODB.Positions()
            db.save_position(page.user, self.stock_symbol, self.position, self.vols, self.rate)


        #page.render('option-chain.html', **page.arg_dict)

    def get_json_object_from_page(self,page):
        #create copies of the json objects
        page.arg_dict['json_option_chain'] = page.request.get('option_chain_hidden')
        page.arg_dict['json_projected_dividends'] = page.request.get('projected_dividends_hidden')
        page.arg_dict['json_vols'] = page.request.get('vols_by_month_hidden')
        page.arg_dict['json_trades_on'] = page.request.get('trades_on_hidden')
        page.arg_dict['json_ordered_expiration_string'] = page.request.get('ordered_expiration_string_hidden')    
        
    def make_non_json_objects(self, page): 
        #create the non json objects
        self.option_chain = json.loads(page.arg_dict['json_option_chain'])
        page.arg_dict['option_chain'] = self.option_chain
        self.projected_dividends = json.loads(page.arg_dict['json_projected_dividends'])
        page.arg_dict['projected_dividends'] = self.make_projected_dividends(page)
        self.make_vols(page)
        page.arg_dict['vols'] = self.vols
        self.trades_on = page.arg_dict['json_trades_on']
        page.arg_dict['trades_on'] = self.trades_on
        self.ordered_expiration_string = json.loads(page.arg_dict['json_ordered_expiration_string'])
        page.arg_dict['ordered_expiration_string'] = self.ordered_expiration_string
        page.arg_dict['ordered_expiration_datetime'] = self.make_ordered_expiration_datetime(page)

    def get_postion_from_page(self,page):
        self.position = {}
        for option in self.option_chain:
            if option[-9] == 'C':
                ending = '_call_position'
            else:
                ending = '_put_position'
            pos = page.request.get(option+ending)
            try:
                pos = int(float(pos))
            except:
                pos = 0
            self.position[option] = pos
        try:
            stock_position = int(float(page.request.get('stock_position')))
        except:
            stock_position = 0
        self.position['stock'] = stock_position       
        page.arg_dict['position'] = self.position
        page.arg_dict['json_position'] = json.dumps(self.position)      


    def make_ordered_expiration_datetime(self,page):
        self.ordered_expiration_datetime = []
        for option in self.option_chain:
            exp_date = self.option_chain[option]['exp_date_str'].split('/')
            exp = datetime.date(int(exp_date[2]),int(exp_date[0]),int(exp_date[1]))
            page.arg_dict['option_chain'][option]['exp_datetime.date'] = exp
            if exp not in self.ordered_expiration_datetime:
                self.ordered_expiration_datetime.append(exp)
        self.ordered_expiration_datetime.sort()
        return self.ordered_expiration_datetime

    def make_projected_dividends(self,page):
        for i in range(len(self.projected_dividends)):
            exp_date = self.projected_dividends[i][0].split('/')
            exp = datetime.date(int(exp_date[2]),int(exp_date[0]),int(exp_date[1]))
            self.projected_dividends[i].append(exp)
        return self.projected_dividends

    def make_vols(self,page):
        self.vols = {}
        for d,v in json.loads(page.arg_dict['json_vols']).items():
            exp = [int(x) for x in d.split('/')]
            exp_date = datetime.date(exp[2],exp[0],exp[1])
            self.vols[exp_date] = v

    def make_option_symbol_list(self,page):
        self.ordered_option_symbol_list = []
        for option in self.option_chain:
            if option[-9] == 'C':
                self.ordered_option_symbol_list.append(option)
        self.ordered_option_symbol_list.sort()
        page.arg_dict['ordered_option_symbol_list'] = self.ordered_option_symbol_list
        page.arg_dict['json_ordered_option_symbol_list'] = json.dumps(self.ordered_option_symbol_list)

    def get_vols_from_page(self,page):
        vols = json.loads(page.arg_dict['json_vols'])
        self.vols = {}
        jvols = {}
        for month in vols:
            spot_vol = page.request.get('spot_vol_'+month)
            slope = page.request.get('slope_'+month)
            smile = page.request.get('smile_'+month)
            try:
                spot_vol = float(spot_vol)
            except:
                spot_vol = .4
            try:
                slope = float(slope)
            except:
                slope = 0
            try:
                smile = float(smile)
            except:
                smile = 0
            exp = [int(x) for x in month.split('/')]
            exp_date = datetime.date(exp[2],exp[0],exp[1])
            self.vols[exp_date] = [spot_vol, slope, smile]
            jvols[month] = [spot_vol, slope, smile]
        page.arg_dict['vols'] = self.vols
        page.arg_dict['json_vols'] = json.dumps(jvols)



class GetNewStock:
    def __init__(self, page):
        pass

class OptionPageHandler(EH.EnhancedHandler):
    def get(self):
        self.render('option-chain.html', **self.arg_dict)

    def post(self):
        self.symbol_submit_btn = self.request.get('symbol_submit')
        self.save_position_btn = self.request.get('save_submit')
        if self.save_position_btn:
            save_pos = SavePosition(self)
        elif self.symbol_submit_btn:
            self.stock_symbol = self.request.get('stock_symbol')
            if self.stock_symbol == '':
                self.arg_dict['error'] = 'Please enter a stock symbol!'
            else:
                self.arg_dict['stock_symbol'] = self.stock_symbol.upper()      
                position = PR.PositionRetriever(self.user, self.stock_symbol)
                if not position.has_error:
                    MakeArgDictPosition(self.arg_dict, position)
                else:
                    self.arg_dict['error'] = "That is not a valid symbol.  Please enter a new symbol"

        self.render('option-chain.html', **self.arg_dict)