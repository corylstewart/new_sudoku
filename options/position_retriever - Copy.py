import option_memcache as OM
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
        self.projected_dividends = None
        self.past_dividends = None
        self.option_chain = None
        self.got_past_div = None
        self.stock_price = None

        if self.stock_symbol in self.mem_pos.optionable_list:
            yq = YQ.YahooQuery()
            self._get_from_memcache()
            if not self.option_chain:
                self._get_from_option_chain_from_occ()
                if not self.option_chain:
                    return
                else:
                    self.mem_pos.put_option_chain(self.option_chain)
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
            #a = self.mem_pos.
            #if not self.vols:
            #    self.vols = {}
            #    for exp in self.mem_pos.option_chain.ordered_expirations_list:
            #        self.vols[exp] = [.4, 0, 0]

    def _get_from_memcache(self):
        self.position = self.mem_pos.position
        self.vols = self.mem_pos.vols
        self.projected_dividends = self.mem_pos.projected_dividends
        self.past_dividends = self.mem_pos.past_dividends
        self.option_chain = self.mem_pos.option_chain

    def _get_from_option_chain_from_occ(self):
        occ = OCC.OccOptionChain(self.stock_symbol)
        self.option_chain = occ

    def _make_empty_position(self):
        #make assertion here
        self.position = {'stock':0}
        for option in self.option_chain.option_chain:
            self.position[option] = 0