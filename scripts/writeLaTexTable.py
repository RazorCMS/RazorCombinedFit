#! /usr/bin/env python
import ConfigParser
import os
import sys
import ROOT as rt
from RazorCombinedFit.Framework import Box
import RootTools

#read the root file with fit results
filename = sys.argv[1]
noext = filename.split('.root')
filelist = noext[0].split('_')
btags = -1
flavor =''
count=0
for descriptor in filelist:
    if descriptor=='ttbar':
        flavor = '$t\\bar{t}$+jets'
    elif descriptor=='Wjets' or descriptor=='Wln':
        flavor = '$W$+jets'
    elif descriptor=='Zll':
        flavor = '$Z$+jets'
    elif descriptor=='Znunu' or descriptor=='Znn':
        flavor = '$Z(\\nu\\bar{\\nu})$+jets'
    elif descriptor=='cocktail' or descriptor=='SMCocktail':
        flavor = 'SM Cocktail'
    if descriptor=='nBtag' or descriptor=='nBtags':
        btags = filelist[count+1]
        if btags =='geq1': btags='$\\geq1$'
    count = count+1

rootfile = rt.TFile(filename)
#open the output file
#outfile = open(sys.argv[2], "w")

BoxName = ["MuEle", "MuMu", "EleEle", "Mu", "Ele", "Had"]

for Box in BoxName:
    vars=[]
    if btags>=0: vars.append('%s %sbtag ' % (flavor,btags))
    else:  vars.append('%s '  % flavor)
    vars.append(' %s ' % Box)
    
    boxDir = rootfile.Get(Box)
    if boxDir is None or not boxDir or not boxDir.InheritsFrom('TDirectory'):
        continue
    
    #read the variables from the workspace
    myws = rootfile.Get(Box+"/Box"+Box+"_workspace")
    fitresult = rootfile.Get(Box+"/fitresult_fitmodel_RMRTree")

    keys = [('pdf1','pdf1pars'),('pdf2','pdf2pars'),('others','otherpars')]    
    #get the final values from the fit
    parlist = fitresult.floatParsFinal()
    fitPars = {}
    for p in RootTools.RootIterator.RootIterator(parlist): fitPars[p.GetName()] = p 
    
    #set the values in the table
    for key, namedset in keys:
        named = myws.set(namedset)

        for v in RootTools.RootIterator.RootIterator(named):
            name = v.GetName()
            checkIfErr = name.split('_')
            if name=='Ntot': continue
            if checkIfErr[len(checkIfErr)-1]=='s': continue
            if fitPars.has_key(name): v = fitPars[v.GetName()]
            if v.getError()==0: vars.append(' $%.2f$ ' % v.getVal())
            else: vars.append(' $%.2f \\pm %.3f$ ' % (v.getVal(),v.getError()))
                  
    print '&'.join(vars)+'\\\\'

#outfile.close()
rootfile.Close()
