class MakeBlanks:
    #this class creates generic blank positions for a new user/symbol combination

    #create a new position with options and stock set to zero
    def make_blank_position(self, option_chain):
        position = {}
        position['stock'] = 0
        for option in option_chain:
            position[option] = 0
        return position

    #create a new dictionary of vols with generic settings
    def make_blank_vols(self, expiry):
        vols = {}
        for ex in expiry:
            vols[ex] = {}
            vols[ex]['vol'] = .4
            vols[ex]['skew'] = 0
            vols[ex]['smile'] = 0
        return vols

