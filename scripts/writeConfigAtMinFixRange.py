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
            if fitPars.has_key(name): v = fitPars[v.GetName()]
            # for now hardcode the ranges of MR, R, Rsq to the loose range
            if name == 'MR':
                vars.append('%s[%.0f,%.0f]' % (v.GetName(),200,3500))
            elif name == 'R':
                vars.append('%s[%.2f,%.0f]' % (v.GetName(),0.2,2))
            elif name == 'Rsq':
                vars.append('%s[%.4f,%.0f]' % (v.GetName(),0.04,4))
            # also adjust the ranges of the parameters MR01st, MR02nd, R01st, R02nd 
            elif name == 'MR01st':
                maxi = 200
                lastVal = v.getVal()
                if lastVal>maxi: lastVal = 190
                vars.append('%s[%.5f,%.3f,%.3f]' % (v.GetName(),lastVal,v.getMin(),maxi))
            elif name == 'MR02nd':
                maxi = 200
                lastVal = v.getVal()
                if lastVal>maxi: lastVal = 190
                vars.append('%s[%.5f,%.3f,%.3f]' % (v.GetName(),lastVal,v.getMin(),maxi))
            elif name == 'R01st':
                maxi = .04
                lastVal = v.getVal()
                if lastVal>maxi: lastVal = .03
                vars.append('%s[%.5f,%.3f,%.3f]' % (v.GetName(),lastVal,v.getMin(),maxi))
            elif name == 'R02nd':
                maxi = .04
                lastVal = v.getVal()
                if lastVal>maxi: lastVal = .03
                vars.append('%s[%.5f,%.3f,%.3f]' % (v.GetName(),lastVal,v.getMin(),maxi))                
            else:
                vars.append('%s[%.5f,%.3f,%.3f]' % (v.GetName(),v.getVal(),v.getMin(),v.getMax()))
        config.set(Box,key,str(vars))
    
config.write(outfile)
outfile.close()
rootfile.Close()
