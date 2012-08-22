import RazorStyle
import RootIterator
import RootFile
import Utils

import ROOT as rt

def getObject(fileName, dsName):
    result = None
    input = None
    closeFile = False
    try:
        input = rt.TFile.Open(fileName)
        result = input.Get(dsName)
        if result is not None and result:
            #if we can make memory resident then do
            if hasattr(result,'SetDirectory'):
                result = result.Clone()
                result.SetDirectory(0)
                closeFile = True
        else:
            result = None    
    finally:
        if input is not None and closeFile: input.Close()
    return result

def getHistNorm(fileName, dsName, cut = None):
    result = None
    input = None
    try:
        input = rt.TFile.Open(fileName)
        result = input.Get(dsName).Integral()
        print result
    finally:
        if input is not None: input.Close()
    return result

def getDataSet(fileName, dsName, cut = None):
    
    result = None    
    input = None
    try:
        input = rt.TFile.Open(fileName)
        result = input.Get(dsName)
        if result is not None and result:
            result.Print('V')
            if cut is not None:
                before = result.numEntries()
                result = result.reduce(rt.RooFit.Cut(cut))
                after = result.numEntries()
                print "Cut '%s' removed %i entries from %s" % (cut,before-after,dsName)
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
