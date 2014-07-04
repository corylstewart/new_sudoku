from options import option_description as od
from options import memcache_and_db as mdb


class MakeAllGreeks:
    'this class queries the memcache and the db and for descriptions not found caclulates the greeks for each description'

    def __init__(self, spot, ordered_list, option_chain, vols, rate, div, use_db = False, use_rounding = False):
        self.spot = spot
        self.ordered_list = ordered_list
        self.option_chain = option_chain
        self.vols = vols
        self.rate = rate
        self.div = div
        self.use_db = use_db
        self.use_rounding = use_rounding
        self.greeks = self.make_all_greeks()

    def make_all_greeks(self):
        options = {}                    #create an empty dict for the symbol/greeks pairs
        still_looking = []              #create the empty list for descriptions we are still looking for
        descriptions = {}               #create an empty dict for description/symbol pairs
        greeks = {}                     #create an empty dict for all of the desciption/greeks pairs to be returned                    
        for option in self.ordered_list:
            opt = od.Option(option, self.spot, self.vols[option], rate = self.rate, div = self.div)      #create an Option object
            options[option] = opt                                                           #create the symbol/Option pair
            still_looking.append(opt.description)                                           #add the desription to the list of still looking
            descriptions[opt.description] = option                                          #create the description/symbol pair
            greeks[option] = {}                                                             #create the symbol/greek pair
            greeks[option]['call'] = {}                                                     #create the call/greek pair
            greeks[option]['put'] = {}                                                      #create the put/greek pair
        memory_greeks = mdb.MdbGreeks()
        mem_greeks = memory_greeks.get_multi_greeks(still_looking, self.use_db)             #query the memcache/DB for the descipitons in still looking
        for description in mem_greeks:                                                      #for the descriptions found in the memcache/DB
            try:
                still_looking.remove(description)                                           #remove the desciption from still looking
            except:
                pass
            option = descriptions[description]                                              
            greeks[option] = mem_greeks[description]                                        #add the symbol/greek pair to the greeks dict
        set_to_mem = {}                                                                     #create empty list for the desciptions that have to be added to memcache/DB
        for description in still_looking:                                                   #for descriptions in still looking
            option = descriptions[description]
            options[option].price()                                                             #using pricer create the option greeks
            greeks[option]['call']['value'] = options[option].optionpricer.greeks.call.value    #set the values of the greeks in the greek dict
            greeks[option]['call']['delta'] = options[option].optionpricer.greeks.call.delta
            greeks[option]['call']['theta'] = options[option].optionpricer.greeks.call.theta
            greeks[option]['call']['gamma'] = options[option].optionpricer.greeks.call.gamma
            greeks[option]['call']['vega'] = options[option].optionpricer.greeks.call.vega
            greeks[option]['put']['value'] = options[option].optionpricer.greeks.put.value
            greeks[option]['put']['delta'] = options[option].optionpricer.greeks.put.delta
            greeks[option]['put']['theta'] = options[option].optionpricer.greeks.put.theta
            greeks[option]['put']['gamma'] = options[option].optionpricer.greeks.put.gamma
            greeks[option]['put']['vega'] = options[option].optionpricer.greeks.put.vega
            greeks[option]['description'] = description                                                                                 ################################added############################
            set_to_mem[description] = greeks[option]                                            #add the description/greeks pair to the dict that will be set in memcache/DB
        mem_opt = mdb.MdbGreeks()
        mem_opt.set_multi_greeks(set_to_mem, self.use_db)                                       #set the description/greeks to the memcache/DB
        return greeks