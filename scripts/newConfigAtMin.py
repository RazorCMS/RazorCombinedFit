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

BoxName = ["MuMu", "MuEle", "Mu", "EleEle", "Ele", "Had", "RazorMultiBoxSim_dir"]
for Box in BoxName:

    boxDir = rootfile.Get(Box)
    if boxDir is None or not boxDir or not boxDir.InheritsFrom('TDirectory'):
        continue
    
    config.add_section(Box)
    
    #read the variables from the workspace
    myws = rootfile.Get(Box+"/Box"+Box+"_workspace")
    #myws.Print()
    keylist = (rootfile.Get(Box)).GetListOfKeys()
    print "next box: "+ Box 
    for obj in keylist:
       
        #print "Attempt to read "+ obj.GetName()
        fitresult = obj.ReadObj()
        
        if not fitresult.InheritsFrom('RooFitResult') : continue
        
        #print "success"
        fitresult.Print()
        if Box =="RazorMultiBoxSim_dir": continue
        
        keys = [('variables','variables'),('pdf1_QCD','pdf1pars_QCD'),('pdf1_TTj','pdf1pars_TTj'),('pdf1_Wln','pdf1pars_Wln'),('pdf1_Zll','pdf1pars_Zll'),('pdf1_Znn','pdf1pars_Znn'),('pdf2_QCD','pdf2pars_QCD'),('pdf2_TTj','pdf2pars_TTj'),('pdf2_Wln','pdf2pars_Wln'),('pdf2_Zll','pdf2pars_Zll'),('pdf2_Znn','pdf2pars_Znn'),('others_QCD','otherpars_QCD'),('others_TTj','otherpars_TTj'),('others_Wln','otherpars_Wln'),('others_Zll','otherpars_Zll'),('others_Znn','otherpars_Znn')]
    
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
        config.set(Box,'variables_range','[\'MR_FULL[300.,3500.]\',\'Rsq_FULL[0.09,0.5]\',\'MR_B1[300.,650.]\',\'Rsq_B1[0.09,0.2]\',\'MR_B2[300.,450.]\',\'Rsq_B2[0.2,0.3]\',\'MR_B3[300.,350.]\',\'Rsq_B3[0.3,0.5]\',\'MR_hC1[650.,1500.]\',\'Rsq_hC1[0.09,0.2]\',\'MR_hC2[450.,1000.]\',\'Rsq_hC2[0.2,0.3]\',\'MR_hC3[350.,800.]\',\'Rsq_hC3[0.3,0.45]\']')
            
config.write(outfile)
outfile.close()
rootfile.Close()




