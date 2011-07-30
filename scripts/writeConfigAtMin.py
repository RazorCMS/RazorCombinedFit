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

BoxName = ["MuMu", "MuEle", "Mu", "EleEle", "Ele", "Had"]
for Box in BoxName:
    
    boxDir = rootfile.Get(Box)
    if boxDir is None or not boxDir or not boxDir.InheritsFrom('TDirectory'):
        continue
    
    config.add_section(Box)
    
    #read the variables from the workspace
    myws = rootfile.Get(Box+"/Box"+Box+"_workspace")
    fitresult = rootfile.Get(Box+"/fitresult_fitmodel_RMRTree")

    keys = [('variables','variables'),('pdf1','pdf1pars'),('pdf2','pdf2pars'),('others','otherpars')]
    
    #get the final values from the fit
    parlist = fitresult.floatParsFinal()
    fitPars = {}
    for p in RootTools.RootIterator.RootIterator(parlist): fitPars[p.GetName()] = p 
    
    #set the values in the config
    for key, namedset in keys:
        named = myws.set(namedset)
        
        vars = []
        for v in RootTools.RootIterator.RootIterator(named):
            name = v.GetName()
            if name.find("_s") != -1: continue
            if fitPars.has_key(name): v = fitPars[v.GetName()]
            if v.getMin() < -1.E10 or v.getMax() > 1.E10: vars.append('%s[%.5f]' % (v.GetName(),v.getVal()))                
            else :
                vars.append('%s[%.5f,%.3f,%.3f]' % (v.GetName(),v.getVal(),v.getMin(),v.getMax()))
                if name != "MR" and name != "Rsq":
                    vars.append('%s_s[%.5f]' % (v.GetName(),v.getError()))
        config.set(Box,key,str(vars))
    
config.write(outfile)
outfile.close()
rootfile.Close()
