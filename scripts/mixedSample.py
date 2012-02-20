#!/usr/bin/env python

import ROOT as rt
import RootTools
import RazorCombinedFit

from optparse import OptionParser

if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-o','--output',dest="output",type="string",default='mixedSample.root',
                  help="Name of the output file to use")
    (options,args) = parser.parse_args()
    
    assert len(args) > 1, 'There must be two input files, one data, one toy' 

    data = args[0]
    toy = args[1]

    def get(fileName):
        inputFile = rt.TFile.Open(fileName)
        return inputFile, inputFile.Get('RMRTree')
    
    cut = "((((( (MR >= 500.000000) && (MR < 800.000000) ) && ( (Rsq >= 0.030000) && (Rsq < 0.090000) )) || (( (MR >= 500.000000) && (MR < 650.000000) ) && ( (Rsq >= 0.090000) && (Rsq < 0.200000) ))) || (( (MR >= 500.000000) && (MR < 600.000000) ) && ( (Rsq >= 0.200000) && (Rsq < 0.300000) ))) || (( (MR >= 500.000000) && (MR < 550.000000) ) && ( (Rsq >= 0.300000) && (Rsq < 0.400000) ))) || (( (MR >= 800.000000) && (MR < 1500.000000) ) && ( (Rsq >= 0.030000) && (Rsq < 0.037500) ))"
    
    dataFile, dataTree = get(data)
    print 'Before',dataTree.numEntries()
    dataTree = dataTree.reduce(cut)
    print 'After',dataTree.numEntries()
    
    toyFile, toyTree = get(toy)
    print 'Toy entries',toyTree.numEntries()
    toyTree = toyTree.reduce(cut)
    print 'After',toyTree.numEntries()
    
    mr = rt.RooRealVar('MR','M_{R} [Gev]',500,4000)
    rsq = rt.RooRealVar('Rsq','R^{2}',0.03,1.0)

    from ROOT import MLMixedSample
    mx = MLMixedSample(10,1000)
    t = mx.testStatistic(dataTree,toyTree,rt.RooArgSet(mr,rsq))
    print t
