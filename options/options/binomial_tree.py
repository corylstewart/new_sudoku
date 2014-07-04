import numpy as np
import black_scholes as bs

'''the Binomail Tree pricing model is based upon the algorithm written by Julien Gosme
his work can be found at http://gosmej1977.blogspot.com/. I have made a few changes
to make it suit my needs a little more but virtually none of this work is mine.  The 
purpose of this web app was to build a position management tool not the actual pricing
model behind it.

Some of the changes made to it we to compensate for the fact that google does not allow
the inclusion of pysci into web apps built on GAE.  So there was some efficiency that
was taken out of his pricing model, and it also lost the ability to price stocks paying
dividends'''

class OptionGreeks:
    'class contains the values of the greeks'
    def __init__(self):
        self.value = None
        self.delta = None
        self.gamma = None
        self.theta = None
        self.vega = None

#create a class including the variable that descibe a
#option so that the pricer can calcualte the greeks
class OptionPricer:
    'class includes the variables needed to price an option as well as the class which contains the greeks'
    def __init__(self, strike, spot, rate, vol, time, binomial_tree_steps = 75, \
                hull_steps = 350, div=[[],[]], regul = 'false', burnIn = 'true', american = 'true'):

        self.strike = float(strike)
        self.spot = float(spot)
        self.rate = float(rate)
        self.vol = float(vol)
        self.time = float(time)
        self.binomial_tree_steps = int(binomial_tree_steps)
        self.hull_steps = int(hull_steps)
        self.div = div 
        self.regul = regul
        self.burnIn = burnIn
        self.american = american
        self.model = ''
        self.call = OptionGreeks()
        self.put = OptionGreeks()
        self.error = False

#for use while debugging
def print_all(o, keyin = ''):
    keylist = o.__dict__.keys()
    keylist.sort()
    for key in keylist:
        if type(o.__dict__[key]) == type(o):
            print_all(o.__dict__[key], keyin = keyin + str(key))
        else:
            print keyin,key,'=', o.__dict__[key]



#binomial tree is used to calculate the greeks of a non dividend stock
#very fast pricer
class BinomialTree(bs.BlackScholes):
    def __init__(self, strike, spot, rate, vol, time, binomial_tree_steps = 75, \
                div=[[],[]], regul = 'false', burnIn = 'true', american = 'true'):

        self.strike = float(strike)
        self.spot = float(spot)
        self.rate = float(rate)
        self.vol = float(vol)
        self.time = float(time)
        self.binomial_tree_steps = int(binomial_tree_steps)
        self.div = div 
        self.regul = regul
        self.burnIn = burnIn
        self.american = american
        self.model = ''
        self.call = OptionGreeks()
        self.put = OptionGreeks()
        self.error = False

        self.binomialtree()

    def binomialtree(self):
        try:
            N = self.binomial_tree_steps
            deltaT = self.time / self.binomial_tree_steps
            dividends = [[],[]]
            if self.burnIn == 'true':
                bi = 2
                self.binomial_tree_steps += bi
            else:
                bi = 0

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
            def expiCallR(stock, strike, vol = self.vol, rate = self.rate, time = deltaT):
                return blackScholes(stock, strike, vol, rate, time, type = 'C')
            def expiPutR(stock, strike, vol = self.vol, rate = self.rate, time = deltaT):
                return blackScholes(stock, strike, vol, rate, time, type = 'P')

            if self.american=='false':
                earlyCall=earlyEuro
                earlyPut=earlyEuro

            if np.size(self.div) > 0 and self.div[0][0] < self.time:
                lastdiv = np.nonzero(np.array(self.div[0][:]) <= self.time)[0][-1]
                dividends[0] = self.div[0][:lastdiv+1]
                dividends[1] = self.div[1][:lastdiv+1]

            if np.size(dividends)>0:
                dividendsStep=np.floor(np.multiply(dividends[0],1/deltaT))
            else:
                dividendsStep=[]    
     
            if np.size(dividends)>0:
                pvdividends=np.sum(dividends[1])
            else:
                pvdividends=0

            dividendsStep = dividendsStep + np.asarray([float(bi) for i in xrange(np.size(dividends[1][:]))])

            S0 = self.spot - pvdividends
            currentDividend = 0

            u = np.exp(self.vol * np.sqrt(deltaT))
            d = 1. / u
            if self.regul == 'true':
                self.binomial_tree_steps = self.binomial_tree_steps - 1

            fsC = np.asarray([0.0 for i in range(self.binomial_tree_steps+1)])
            fsP = np.asarray([0.0 for i in range(self.binomial_tree_steps+1)])
            fs2 = np.asarray([(S0 * u**j * d**(self.binomial_tree_steps-j)) for j in xrange(self.binomial_tree_steps +1)])
            fs3 = np.asarray([self.strike for i in xrange(self.binomial_tree_steps+1)])

            a = np.exp(self.rate * deltaT)
            p = (a - d) / (u - d)
            oneMinusP = 1. - p

            if self.regul == 'true':
                fsC[:] = expiCallR(fs2,fs3)
                fsP[:] = expiPutR(fs2,fs3)
            else:
                fsC[:] = expiCall(fs2,fs3)
                fsP[:] = expiPut(fs2,fs3)
         
            for i in xrange(self.binomial_tree_steps-1, -1+bi, -1):
                fsC[:-1]=np.exp(-self.rate * deltaT) * (p * fsC[1:] + oneMinusP * fsC[:-1])
                fsP[:-1]=np.exp(-self.rate * deltaT) * (p * fsP[1:] + oneMinusP * fsP[:-1])

                fs2[:]=fs2[:]*u
               
                fsC[:]=earlyCall(fsC[:],fs2[:],fs3[:])
                fsP[:]=earlyPut(fsP[:],fs2[:],fs3[:])

            if self.burnIn=='true':
                self.call.value=fsC[bi/2]
                self.put.value=fsP[bi/2]
                self.call.delta=(fsC[bi/2+1]-fsC[bi/2-1])/(fs2[bi/2+1]-fs2[bi/2-1])
                self.put.delta=(fsP[bi/2+1]-fsP[bi/2-1])/(fs2[bi/2+1]-fs2[bi/2-1])
                s2a=fs2[bi/2+1]-fs2[bi/2]
                s2b=fs2[bi/2]-fs2[bi/2-1]
                self.call.gamma=((fsC[bi/2+1]-fsC[bi/2])/s2a +(-fsC[bi/2]+fsC[bi/2-1])/s2b)/((fs2[bi/2+1]-fs2[bi/2-1])/2)
                self.put.gamma=((fsP[bi/2+1]-fsP[bi/2])/s2a +(-fsP[bi/2]+fsP[bi/2-1])/s2b)/((fs2[bi/2+1]-fs2[bi/2-1])/2)
                self.call.theta = self.black_scholes_theta(self.strike, self.spot, self.vol, self.rate, self.time, 'C')
                self.put.theta = self.black_scholes_theta(self.strike, self.spot, self.vol, self.rate, self.time, 'P')
                self.call.vega = self.black_scholes_vega(self.strike, self.spot, self.vol, self.rate, self.time, 'C')
                self.put.vega = self.black_scholes_vega(self.strike, self.spot, self.vol, self.rate, self.time, 'P')
                self.model = 'BT'
    
            else:                
                self.call.value=fsC[0]
                self.put.value=fsP[0]
        except:
            self.error = True


#k = BinomialTree(100, 100, .005, .4, 1)
#print_all(k)

