#!/usr/bin/env python

import ROOT as rt
import RootTools
import RazorCombinedFit

from optparse import OptionParser

if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-o','--output',dest="output",type="string",default='combinedFitResult.root',
                  help="Name of the output file to use",metavar='FILE')
    parser.add_option('--bjet',dest="bjet",type="string",default=None,
                  help="Name of the input file for the BJet box",metavar='FILE')    
    parser.add_option('--ele',dest="ele",type="string",default=None,
                  help="Name of the input file for the Ele box",metavar='FILE')    
    parser.add_option('--mu',dest="mu",type="string",default=None,
                  help="Name of the input file for the Mu box",metavar='FILE')    
    parser.add_option('--had',dest="had",type="string",default=None,
                  help="Name of the input file for the Had box",metavar='FILE')      
    (options,args) = parser.parse_args()
   # if options.bjet is None or options.had is None:
   #     parser.error("Need to specify both the --bjet and --had options")

    def getBoxContents(box, store):
        rt.gDirectory.cd(box)
        keys = rt.gDirectory.GetListOfKeys()
        for k in RootTools.RootIterator.RootIterator(keys):
            name = k.GetName()
            o = rt.gDirectory.Get(name)
            if o is None or not o: continue
            store.add(o,name=name,dir=box)
        rt.gDirectory.cd()
    
    store = RootTools.RootFile.RootFile(options.output)

    if not(options.had is None) :
        hadFile = rt.TFile.Open(options.had)
        getBoxContents('BJetLS',store)
        hadFile = rt.TFile.Open(options.had)
        getBoxContents('BJetHS',store)

    if not(options.bjet is None) :
        bjetFile = rt.TFile.Open(options.bjet)
        getBoxContents('BJet',store)

    if not(options.ele is None) :
        eleFile = rt.TFile.Open(options.ele)
        getBoxContents('Ele',store)

    if not(options.mu is None) :
        muFile = rt.TFile.Open(options.mu)
        getBoxContents('Mu',store)


    store.write()
