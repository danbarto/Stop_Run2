import logging
logger = logging.getLogger(__name__)

class xSecSusy:
    def __init__(self):
        from stops_13TeV import xsecNNLL as stop13TeV
        self.xSec = {
            'stop13TeV':stop13TeV
        }

    def getXSec(self, mass, sigma=0, channel='stop13TeV'):
        from math import log, exp
        if self.xSec[channel].has_key(mass):
            return self.xSec[channel][mass][0]+sigma*self.xSec[channel][mass][1]*self.xSec[channel][mass][0]
        else: #Interpolate
            masses = self.xSec[channel].keys()
            lower = max([x for x in masses if x < mass])
            upper = min([x for x in masses if x > mass])

            log_x_sec_lower = log(self.xSec[channel][lower][0]+sigma*self.xSec[channel][lower][1]*self.xSec[channel][lower][0])
            log_x_sec_upper = log(self.xSec[channel][upper][0]+sigma*self.xSec[channel][upper][1]*self.xSec[channel][upper][0])

            res = exp( log_x_sec_lower + (mass - lower)/float(upper-lower)*(log_x_sec_upper - log_x_sec_lower)  )
            logger.info( "Log-interpolating SUSY xSec: mass %3.2f using sigma %3.2f m=%3.2f (%3.2f) and m=%3.2f (%3.2f). Result is %3.2f", mass, sigma, lower, exp(log_x_sec_lower), upper, exp(log_x_sec_upper), res )
            return res
            
            
