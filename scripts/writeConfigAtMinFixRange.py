#! /usr/bin/env python
import ConfigParser
import os
import sys
import ROOT as rt
from RazorCombinedFit.Framework import Box
import RootTools

#read the root file with fit results
filename = sys.argv[1]
rootfile = rt.TFile(filename)
#open the output file
outfile = open(sys.argv[2], "w")

config = ConfigParser.ConfigParser()

BoxName = ["MuEle", "MuMu", "EleEle", "MuTau", "Mu", "EleTau", "Ele", "Jet", "TauTauJet", "MultiJet"]
for Box in BoxName:
    
    boxDir = rootfile.Get(Box)
    if boxDir is None or not boxDir or not boxDir.InheritsFrom('TDirectory'):
        continue
    
    config.add_section(Box)
    
    #read the variables from the workspace
    myws = rootfile.Get(Box+"/Box"+Box+"_workspace")
    fitresult = rootfile.Get(Box+"/independentFR")

    keys = [('pdf_TTj1b','pdfpars_TTj1b'), ('others_TTj1b','otherpars_TTj1b'), ('btag_TTj1b','btagpars_TTj1b'),
            ('pdf_TTj2b','pdfpars_TTj2b'), ('others_TTj2b','otherpars_TTj2b'), ('btag_TTj2b','btagpars_TTj2b'),
            ('pdf_Vpj','pdfpars_Vpj'), ('others_Vpj','otherpars_Vpj'), ('btag_Vpj','btagpars_Vpj'),]
    myws.Print()
    #get the final values from the fit
    parlist = fitresult.floatParsInit()
    fitPars = {}
    for p in RootTools.RootIterator.RootIterator(parlist):
        fitPars[p.GetName()] = p 
    
    #set the values in the config
    for key, namedset in keys:
        named = myws.set(namedset)
        
        vars = []
        for v in RootTools.RootIterator.RootIterator(named):
            name = v.GetName()
            if fitPars.has_key(name):
                v = fitPars[v.GetName()]
                if name.find('R0_')!=-1 or name.find('n_')!=-1 or name.find('b_')!=-1:
                    vars.append('%s[%.5f]' % (v.GetName(),v.getVal()))
                elif name.find('Ntot_')!=-1 or name.find('f')!=-1:
                    vars.append('%s[%.5f,%.3f,%.3f]' % (v.GetName(),v.getVal(),v.getMin(),v.getMax()))
        config.set(Box,key,str(vars))
    
config.write(outfile)
outfile.close()
rootfile.Close()
