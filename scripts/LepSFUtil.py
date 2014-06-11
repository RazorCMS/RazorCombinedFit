
from math import sqrt

## class LepSFUtil( object ):
    
##     def __init__(self, flavor):
##         print 'initializing LepSFUtil'
##         self.flavor = flavor


##     def getScaleFactor(self, eta, errDir):
##         pass

def getScaleBinned(pt, ptBins, payload):
    """Generic helper function for the payloads"""
    for i in xrange(len(ptBins) -1):
        if (pt > ptBins[i]) and (pt <= ptBins[i+1]):
            return payload[i]
    return payload[-1]

class MuSFUtil( object ):
    ###ID
    def getScaleFactorID(self, pt, eta, errDir):
        if eta < 0.9 :
            return 0.9937 * ( 1 + errDir*self.getScaleFactorIDError() )
        elif eta < 1.2 : 
            return 0.9909 * ( 1 + errDir*self.getScaleFactorIDError() )
        else :
            return 0.9980 * ( 1 + errDir*self.getScaleFactorIDError() )
        
    def getScaleFactorIDError(self):
        return 0.05

    ###iso
    def getScaleFactorIso(self, pt, eta, errDir):
        if eta < 0.9 :
            return 0.9955 * ( 1 + errDir*self.getScaleFactorIsoError() )
        elif eta < 1.2 :
            return 0.9994 * ( 1 + errDir*self.getScaleFactorIsoError() )
        else :
            return 1.0033 * ( 1 + errDir*self.getScaleFactorIsoError() )
      
    def getScaleFactorIsoError(self):
       return 0.02

    ###trigger
    def getScaleFactorTrigger(self, pt, eta, errDir):
        if eta < 0.9 :
            return 0.9809 * ( 1 + errDir*self.getScaleFactorTriggerError() )
        elif eta < 1.2 :
            return 0.9653 * ( 1 + errDir*self.getScaleFactorTriggerError() )
        else :
            return 0.9932 * ( 1 + errDir*self.getScaleFactorTriggerError() )
      
    def getScaleFactorTriggerError(self):
        return 0.02
  
    ###overall
 
    def getScaleFactor(self, pt, eta, errDir):
        return self.getScaleFactorID(pt, eta, errDir), self.getScaleFactorIso(pt, eta, errDir), self.getScaleFactorTrigger(pt, eta, errDir)


################################################################################################################
#             Ele
################################################################################################################


class EleSFUtil( object ):

    def __init__(self):
        self.ptBins = [30, 40, 50, 200]
    
    def getScaleFactor(self, pt, eta, errDir):
        if eta < 0.8 :
            payload = [0.979, 0.984, 0.983]
            return getScaleBinned(pt, self.ptBins, payload) * ( 1 + errDir*self.getScaleFactorError( pt, eta ) )
        elif eta < 1.442 :
            payload = [0.961, 0.972, 0.977]
            return getScaleBinned(pt, self.ptBins, payload) * ( 1 + errDir*self.getScaleFactorError( pt, eta ) )
        elif eta < 1.556 :
            payload = [0.983, 0.957, 0.978]
            return getScaleBinned(pt, self.ptBins, payload) * ( 1 + errDir*self.getScaleFactorError( pt, eta ) )
        elif eta < 2.0 :
            payload = [0.962, 0.985, 0.986]
            return getScaleBinned(pt, self.ptBins, payload) * ( 1 + errDir*self.getScaleFactorError( pt, eta ) )
        elif eta < 2.5 :
            payload = [1.002, 0.999, 0.995]
            return getScaleBinned(pt, self.ptBins, payload) * ( 1 + errDir*self.getScaleFactorError( pt, eta ) )
      
    def getScaleFactorError(self, pt, eta):
        if eta < 0.8 :
            payload = [sqrt(0.002*0.002 + 0.001*0.001), 0.001, 0.001]
            return getScaleBinned(pt, self.ptBins, payload) 
        elif eta < 1.442 :
            payload = [sqrt(0.002*0.002 + 0.005*0.005), sqrt(2)*0.001, sqrt(0.001*0.001 + 0.004*0.004) ]
            return getScaleBinned(pt, self.ptBins, payload)
        elif eta < 1.556 :
            payload = [sqrt(0.008*0.008 + 0.002*0.002), 0.004, sqrt(0.007*0.007 + 0.004*0.004)]
            return getScaleBinned(pt, self.ptBins, payload) 
        elif eta < 2.0 :
            payload = [sqrt(0.003*0.003 + 0.002*0.002), sqrt(2)*0.001, sqrt(0.002*0.002 + 0.005*0.005)]
            return getScaleBinned(pt, self.ptBins, payload)
        elif eta < 2.5 :
            payload = [sqrt(0.004*0.004 + 0.001*0.001), sqrt(2)*0.002, sqrt(0.003*0.003 + 0.001*0.001)]
            return getScaleBinned(pt, self.ptBins, payload) 
      
         
##         return 0.05

  
##     ###overall
 
##     def getScaleFactor(self, pt, eta, errDir):
##         return self.getScaleFactorID(pt, eta, errDir), self.getScaleFactorIso(pt, eta, errDir), self.getScaleFactorTrigger(pt, eta, errDir)
