import RootIterator
import RootFile
import Utils

import ROOT as rt

def getDataSet(fileName, dsName, cut = None):
    
    result = None    
    input = None
    try:
        input = rt.TFile.Open(fileName)
        result = input.Get(dsName)
        result.Print('V')
        if result is not None and cut is not None:
            print cut
            result = result.reduce(rt.RooFit.Cut(cut))
    finally:
        if input is not None: input.Close()
    return result

def writeToyResults(study, fileName):
    
    out = None
    try:
        out = rt.TFile.Open(fileName,'RECREATE')
        study._fitParData.write('%s.dat' % fileName)
        variables = study._fitParData.get()
        variables.Write('variables')
    finally:
        if out is not None: out.Close()
        
def readToyResults(fileName):
    
    args = None
    input = None
    try:
        input = rt.TFile.Open(fileName)
        args = input.Get('variables')
    finally:
        if input is not None: input.Close()
    args.Print("V")
    
    data = rt.RooDataSet.read('%s.dat' % fileName, rt.RooArgList(args))
    return data