import numpy as np
import math


class BlackScholes:

    #black scholes is used by the bimolial tree if I could get the regularization to work
    #but without scipy that seems unlikely
    def black_scholes_call_or_put(self, strike, spot, vol, rate, time, type):
        d1 = (np.log(spot / strike) + (rate + vol**2 / 2) * time)/(vol * np.sqrt(time))   
        d2 = (np.log(spot / strike) + (rate - vol**2 / 2) * time) / (vol * np.sqrt(time))
        if type=="C":
            return spot * self.cdf(d1) - strike * np.exp(-rate * time) * self.cdf(d2)
        else:
           return spot * np.exp(-rate * time) * self.cdf(-d2) - spot * self.cdf(-d1)

    #cumulative distribution function used by black scholes
    def cdf(self, x):
        return (1.0+math.erf(x / math.sqrt(2.0))) / 2.0


    #returns the value of a call and a put using black scholes for use in
    #calculating the greeks using interpolation
    def black_scholes_call_and_put(self, strike, spot, vol, rate, time):
        d1 = (np.log(spot / strike) + (rate + vol**2 / 2) * time)/(vol * np.sqrt(time))   
        d2 = (np.log(spot / strike) + (rate - vol**2 / 2) * time) / (vol * np.sqrt(time))
        call = spot * self.cdf(d1) - strike * np.exp(-rate * time) * self.cdf(d2)
        put = spot * np.exp(-rate * time) * self.cdf(-d2) - spot * self.cdf(-d1)
        return call, put

    #simple interpolation
    def interpolate(self, arg1, arg2, diff):
        return (arg1-arg2)/diff

    #calculate the vega by interpolating over a slight change in vol
    def black_scholes_vega(self, strike, spot, vol, rate, time, type):
        vol_diff = vol * .005
        price1 = self.black_scholes_call_or_put(strike, spot, vol, rate, time, type)
        price2 = self.black_scholes_call_or_put(strike, spot, vol+vol_diff, rate, time, type)
        return self.interpolate(price2, price1, vol_diff)/100

    #calculate the theta by interpolating over a slight change in time
    def black_scholes_theta(self, strike, spot, vol, rate, time, type):
        if time*365 < 30 and time*365 > 10:
            t_diff = .5/365
            diff = .5
        elif time*365 <= 10:
            t_diff = .25/365
            diff = .25
        else:
            t_diff = 1/365.
            diff = 1
        price1 = self.black_scholes_call_or_put(strike, spot, vol, rate, time, type)
        price2 = self.black_scholes_call_or_put(strike, spot, vol, rate, time-t_diff, type)
        return self.interpolate(price2, price1, diff)

    #calculate the delta by interpolating over a slight change in spot
    def black_scholes_delta(self, strike, spot, vol, rate, time, type):
        price1 = self.black_scholes_call_or_put(strike, spot, vol, rate, time, 'C')
        price2 = self.black_scholes_call_or_put(strike, spot*1.001, vol, rate, time, 'C')
        if type == 'C':
            return self.interpolate(price2,price1,spot*.001)
        else:
            return self.interpolate(price2,price1,spot*.001)-1

    #calculate the gamma by interpolating over a slight change in delta
    def black_scholes_gamma(self, strike, spot, vol, rate, time, type):
        delta1 = self.black_scholes_delta(strike, spot, vol, rate, time, type)
        delta2 = self.black_scholes_delta(strike, spot*1.001, vol, rate, time, type)
        return abs(self.interpolate(delta2,delta1,spot*.001))
