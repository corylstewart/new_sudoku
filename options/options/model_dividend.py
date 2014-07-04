import datetime

class ModelDividend:
    'this class creates a list of list that represent the div for use in the option pricing models'

    def make_model_dividend(self, projected_dividends):
        today = datetime.date.today()               #set today datetime
        divs = []
        for exp in projected_dividends:
            ex = exp[2]                                     #get the ex date
            div = exp[1]                                    #get the div amount
            if ex > today:                                  #if the div has not happened
                divs.append([(ex-today).days/365.0,div])    #append divs with the time till ex and value
        divs.sort()
        return divs
