import numpy as np
import math
import black_scholes as bs

'''the hull pricing model is based upon the algorithm written by Julien Gosme
his work can be found at http://gosmej1977.blogspot.com/. I have made a few changes
to make it suit my needs a little more but virtually none of this work is mine.  The 
purpose of this web app was to build a position management tool not the actual pricing
model behind it.'''


#create a class for the greeks
class OptionGreeks:
    'class contains the values of the greeks'
    def __init__(self):
        self.value = None
        self.delta = None
        self.gamma = None
        self.theta = None
        self.vega = None

#for use while debugging
def print_all(o, keyin = ''):
    keylist = o.__dict__.keys()
    keylist.sort()
    for key in keylist:
        if type(o.__dict__[key]) == type(o):
            print_all(o.__dict__[key], keyin = keyin + str(key))
        else:
            print keyin,key,'=', o.__dict__[key]

#create a class including the variable that descibe a
#option so that the pricer can calcualte the greeks
class Hull(bs.BlackScholes):
    'class includes the variables needed to price an option as well as the class which contains the greeks'
    def __init__(self, strike, spot, rate, vol, time, hullsteps = 350, div=[[],[]], american = 'true'):
        self.strike = float(strike)
        self.spot = float(spot)
        self.rate = float(rate)
        self.vol = float(vol)
        self.time = float(time)
        self.hullsteps = int(hullsteps)
        self.div = div 
        self.american = american
        self.model = ''
        self.call = OptionGreeks()
        self.put = OptionGreeks()
        self.error = False

        self.hull('C')
        self.hull('P')

    #hull is used to price the divdend paying stocks both slow and the greeks
    #excluding price are not reliable
    def hull(self, type):
        try:
            S0 = self.spot
            def expiCall(stock,strike):
                return(np.maximum(stock-strike,0))
    
            def expiPut(stock,strike):
                return(np.maximum(strike-stock,0))
    
            def earlyCall(Option,stock,strike):
                return(np.maximum(stock-strike,Option))
    
            def earlyEuro(Option,stock,strike):
                return(np.maximum(Option,0))
    
            def earlyPut(Option,stock,strike):
                return(np.maximum(strike-stock,Option))    
  
            if type=='C':
                expi=expiCall
                early=earlyCall
            else:
                expi=expiPut   
                early=earlyPut
    
            if self.american=='false':
                early=earlyEuro
    
            deltaT = float(self.time) / self.hullsteps
            dividends=[[],[]]
    
            if (np.size(self.div)>0 and self.div[0][0]<self.time) :
                lastdiv=np.nonzero(np.array(self.div[0][:])<=self.time)[0][-1]
                dividends[0]=self.div[0][:lastdiv+1]        
                dividends[1]=self.div[1][:lastdiv+1] 
      
            if np.size(dividends)>0:
                dividendsStep=np.floor(np.multiply(dividends[0],1/deltaT))
            else:
                dividendsStep=[]
         
            if np.size(dividends)>0:
                pvdividends=np.sum(np.multiply(dividends[1],np.exp(np.multiply(dividendsStep,-self.rate*deltaT))))
            else:
                pvdividends=0

            S0=S0-pvdividends
            currentDividend=0   

            u = np.exp(self.vol * np.sqrt(deltaT))
            d = 1.0 / u
 
            fs =  np.asarray([0.0 for i in xrange(self.hullsteps + 1)])
        
            fs2 = np.asarray([(S0 * u**j * d**(self.hullsteps - j)) for j in xrange(self.hullsteps + 1)])
    
            fs3 =np.asarray( [float(self.strike) for i in xrange(self.hullsteps + 1)])
    
            a = np.exp(self.rate * deltaT)
            p = (a - d)/ (u - d)
            oneMinusP = 1.0 - p
 
            fs[:] = expi(fs2,fs3)
    
            for i in xrange(self.hullsteps-1, -1, -1):
               fs[:-1]=np.exp(-self.rate * deltaT) * (p * fs[1:] + oneMinusP * fs[:-1])
               fs2[:]=fs2[:]*u
               currentDividend=currentDividend/a
       
               if (i in dividendsStep):
                    div=dividends[1][np.nonzero(dividendsStep==(i))[0]]            
                    currentDividend=currentDividend+div
                
               fs[:]=early(fs[:],fs2[:]+currentDividend,fs3[:])
    
            self.model='Hull'
            if type == 'C':
                self.call.value = fs[0]
                self.call.delta = self.black_scholes_delta(self.strike, self.spot, self.vol, self.rate, self.time, 'C')
                self.call.gamma = self.black_scholes_gamma(self.strike, self.spot, self.vol, self.rate, self.time, 'C')
                self.call.theta = self.black_scholes_theta(self.strike, self.spot, self.vol, self.rate, self.time, 'C')
                self.call.vega = self.black_scholes_vega(self.strike, self.spot, self.vol, self.rate, self.time, 'C')
            elif type == 'P':
                self.put.value = fs[0]
                self.put.delta = self.black_scholes_delta(self.strike, self.spot, self.vol, self.rate, self.time, 'P')
                self.put.gamma = self.black_scholes_gamma(self.strike, self.spot, self.vol, self.rate, self.time, 'P')
                self.put.theta = self.black_scholes_theta(self.strike, self.spot, self.vol, self.rate, self.time, 'P')
                self.put.vega = self.black_scholes_vega(self.strike, self.spot, self.vol, self.rate, self.time, 'P')
            else:
                return
        except:
            self.error = True