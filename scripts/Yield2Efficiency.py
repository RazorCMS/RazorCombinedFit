from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Box

if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-y','--yield',dest="yield_estimate",default=0.,type=float,
                  help="The estimated yield")
    parser.add_option('-e','--error',dest="error",default=0.,type=float,
                  help="The estimated yield error")
    parser.add_option('-l','--lumi',dest="lumi",default=1000.,type=float,
                  help="The estimated yield error")
    parser.add_option('-f','--flavour',dest="flavour",default='TTj',
                  help="The flavour of MC used as input")
    (options,args) = parser.parse_args()
    
    y = options.yield_estimate
    ye = options.error
    l = options.lumi
    cross_sections = Box.getCrossSections()
    c = cross_sections[options.flavour]
    
    def getEff(estimate):
        return estimate/(c*l)
    
    central = getEff(y)
    uncert = max( abs(central - getEff(y+ye)),abs(central - getEff(y-ye)) )
    
    print "['Lumi[%f]','Epsilon_%s[%f,0,1]', 'Epsilon_%s_s[%f]']" % (l,options.flavour,central,options.flavour,uncert)