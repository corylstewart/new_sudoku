from google.appengine.api import memcache
import occ_query as OCC

class OptionsMemcache:
    def __init__(self, user, stock_symbol):
        self.user = user
        self.stock_symbol = stock_symbol
        self.optionable_type = 'optionable_list'
        self.position_type = 'position'
        self.vols_type = 'vols'
        self.projected_dividends_type = 'projected_dividends'
        self.past_dividends_type = 'past_dividends'
        self.option_chain_type = self.stock_symbol + '_option_chain'
        self.optionable_list = self.get_optionable_list()
        self.position = None
        self.vols = None
        self.projected_dividends = None
        self.past_dividends = None
        self.option_chain = None

        if self.stock_symbol in self.optionable_list:
            self.position = self.get_user_type(self.position_type)
            self.vols = self.get_user_type(self.vols_type)
            self.projected_dividends = self.get_user_type(self.projected_dividends_type)
            self.past_dividends = self.get_user_type(self.past_dividends_type)
            self.option_chain = self.get_option_chain()


    def get_optionable_list(self):
        optionable = memcache.get(self.optionable_type)
        if not optionable:
            optionable = OCC.OccOptionableList().optionable_list
            if optionable:
                memcache.set(self.optionable_type, optionable, 25200)
        return optionable

    def make_memcache_string(self,type):
        return self.user + '_' + self.stock_symbol + '_' + type

    def get_user_type(self, type):
        return memcache.get(self.make_memcache_string(type))

    def put_user_of_type(self, value, type):
        memcache.set(self.make_memcache_string(type), value, 25200)

    def get_option_chain(self):
        return memcache.get(self.option_chain_type)

    def put_option_chain(self, option_chain):
        memcache.set(self.option_chain_type, option_chain, 25200)

    def remove_user_position(self):
        for key, value in self.types.items():
            memcache.delete(self.make_memcache_string(value))


