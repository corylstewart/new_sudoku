import option_memcache as OM
import option_db as ODB
import occ_query as OCC
import yahoo_query as YQ


class PositionRetriever:
    def __init__(self, user, stock_symbol):
        self.user = user
        self.stock_symbol = stock_symbol.upper()
        self.mem_pos = OM.OptionsMemcache(self.user,self.stock_symbol)
        self.optionable_list = None
        self.position = None
        self.vols = None
        self.vols_str = None
        self.projected_dividends = None
        self.past_dividends = None
        self.option_chain = None
        self.got_past_div = None
        self.stock_price = None
        self.db_position = None
        self.db_vols = None
        self.db_rate = None
        self.has_error = False

        if self.stock_symbol not in self.mem_pos.optionable_list:
            self.has_error = True
        else:
            yq = YQ.YahooQuery()
            self._get_from_memcache()
            if self.mem_pos.option_chain:
                self.option_chain = self.mem_pos.option_chain
            else:
                self._get_option_chain_from_occ()
                if self.option_chain:
                    self.mem_pos.put_option_chain(self.option_chain)
                else:
                    return
            if not self.position:
                self._make_empty_position()
                self.mem_pos.put_user_of_type(self.position, self.mem_pos.position_type)
            if not self.projected_dividends or not self.past_dividends:
                self.past_dividends, self.got_past_div = yq.get_dividend(self.stock_symbol)
            if self.got_past_div:
                self.mem_pos.put_user_of_type(self.past_dividends, self.mem_pos.past_dividends_type)
                self.projected_dividends = yq.create_div_projections(self.past_dividends)
                self.mem_pos.put_user_of_type(self.projected_dividends, self.mem_pos.projected_dividends_type)
            self.stock_price = yq.stock_px(self.stock_symbol)
            if not self.stock_price:
                stock_price = 50.00
            if not self.vols:
                self.vols = {}
                for exp in self.option_chain.ordered_expirations_list:
                    self.vols[exp] = [.4, 0, 0]
                self.mem_pos.put_user_of_type(self.vols, self.mem_pos.vols_type)
            self.rate = .005
            self._get_position_from_db()
            if self.db_position:
                self.position = self.db_position
            if self.db_vols:
                self.vols = self.db_vols
            if self.db_rate:
                self.rate = self.db_rate

            self._make_vol_str()

    def _get_from_memcache(self):
        self.position = self.mem_pos.position
        self.vols = self.mem_pos.vols
        self.projected_dividends = self.mem_pos.projected_dividends
        self.past_dividends = self.mem_pos.past_dividends
        self.option_chain = self.mem_pos.option_chain

    def _get_option_chain_from_occ(self):
        self.option_chain = OCC.OccOptionChain(self.stock_symbol)
        

    def _make_empty_position(self):
        #make assertion here
        self.position = {'stock':0}
        for option in self.option_chain.option_chain:
            self.position[option] = 0

    def _get_position_from_db(self):
        p = ODB.Positions().retrieve_position(self.user, self.stock_symbol)
        if p:
            self.db_position = p.position
            self._fix_db_position()
            self.db_vols = p.vols
            self._fix_db_vols()
            self.db_rate = p.rate

    def _fix_db_position(self):
        for option in self.option_chain.option_chain:
            if option not in self.db_position:
                self.db_position[option] = 0
        for option, position in self.db_position.items():
            if option not in self.option_chain.option_chain and option<>'stock':
                del self.db_position[option]

    def _fix_db_vols(self):
        for exp in self.vols:
            if exp not in self.db_vols:
                self.db_vols[exp] = [.4,0,0]
        for exp,vols in self.db_vols.items():
            if exp not in vols:
                del self.db_vols[exp]


    def _make_vol_str(self):
        self.vols_str = {}
        for i in range(len(self.option_chain.ordered_expirations_list)):
            self.vols_str[self.option_chain.ordered_expirations_string[i]] = \
                self.vols[self.option_chain.ordered_expirations_list[i]]