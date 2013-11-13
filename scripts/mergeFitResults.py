#!/usr/bin/env python

import ROOT as rt
import RootTools
import RazorCombinedFit

from optparse import OptionParser

if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-o','--output',dest="output",type="string",default='combinedFitResult.root',
                  help="Name of the output file to use",metavar='FILE')
    parser.add_option('--Jet2b',dest="Jet2b",type="string",default=None,
                  help="Name of the input file for the Jet2b box",metavar='FILE')    
    parser.add_option('--MultiJet',dest="MultiJet",type="string",default=None,
                  help="Name of the input file for the MultiJet box",metavar='FILE')    
    parser.add_option('--MuEle',dest="MuEle",type="string",default=None,
                  help="Name of the input file for the MuEle box",metavar='FILE')     
    parser.add_option('--MuMu',dest="MuMu",type="string",default=None,
                  help="Name of the input file for the MuMu box",metavar='FILE')     
    parser.add_option('--EleEle',dest="EleEle",type="string",default=None,
                  help="Name of the input file for the EleEle box",metavar='FILE')     
    parser.add_option('--MuJet',dest="MuJet",type="string",default=None,
                  help="Name of the input file for the MuJet box",metavar='FILE')     
    parser.add_option('--MuMultiJet',dest="MuMultiJet",type="string",default=None,
                  help="Name of the input file for the MuMultiJet box",metavar='FILE')     
    parser.add_option('--EleJet',dest="EleJet",type="string",default=None,
                  help="Name of the input file for the EleJet box",metavar='FILE')     
    parser.add_option('--EleMultiJet',dest="EleMultiJet",type="string",default=None,
                  help="Name of the input file for the EleMultiJet box",metavar='FILE')  
    (options,args) = parser.parse_args()
    if all(x is None for x in [options.MultiJet, options.Jet2b, options.MuEle, 
                               options.MuMu, options.EleEle, options.MuMultiJet, 
                               options.MuJet, options.EleMultiJet, options.EleJet]):
        parser.error("Need to specify at least one box option")

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

    if options.MultiJet is not None:
        MultiJetFile = rt.TFile.Open(options.MultiJet)
        getBoxContents('MultiJet',store)
    
    if options.Jet2b is not None:
        Jet2bFile = rt.TFile.Open(options.Jet2b)
        getBoxContents('Jet2b',store)
    
    if options.MuEle is not None:
        MuEleFile = rt.TFile.Open(options.MuEle)
        getBoxContents('MuEle',store) 
    
    if options.MuMu is not None:
        MuMuFile = rt.TFile.Open(options.MuMu)
        getBoxContents('MuMu',store)
    
    if options.EleEle is not None:
        EleEleFile = rt.TFile.Open(options.EleEle)
        getBoxContents('EleEle',store)
    
    if options.EleJet is not None:
        EleJetFile = rt.TFile.Open(options.EleJet)
        getBoxContents('EleJet',store)
    
    if options.EleMultiJet is not None:
        EleMultiJetFile = rt.TFile.Open(options.EleMultiJet)
        getBoxContents('EleMultiJet',store)

    if options.MuJet is not None:
        MuJetFile = rt.TFile.Open(options.MuJet)
        getBoxContents('MuJet',store)
    
    if options.MuMultiJet is not None:
        MuMultiJetFile = rt.TFile.Open(options.MuMultiJet)
        getBoxContents('MuMultiJet',store)
    
    store.write()
