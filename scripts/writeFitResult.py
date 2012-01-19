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
#outfile = open(sys.argv[2], "w")
config = ConfigParser.ConfigParser()

BoxName = ["MuMu", "MuEle", "Mu", "EleEle", "Ele", "Had", 'BJET', "RazorMultiBoxSim_dir"]
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
        fitresult.Print("v")
        if Box =="RazorMultiBoxSim_dir": continue
        
        keys = [('variables','variables'),('pdf1_TTj','pdf1pars_TTj'),('pdf1_Wln','pdf1pars_Wln'),('pdf1_Zll','pdf1pars_Zll'),('pdf1_Znn','pdf1pars_Znn'),('pdf2_TTj','pdf2pars_TTj'),('pdf2_Wln','pdf2pars_Wln'),('pdf2_Zll','pdf2pars_Zll'),('pdf2_Znn','pdf2pars_Znn'),('others_TTj','otherpars_TTj'),('others_Wln','otherpars_Wln'),('others_Zll','otherpars_Zll'),('others_Znn','otherpars_Znn')]
    
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
        config.set(Box,'variables_range','[\'MR_FULL[300.,3500.]\',\'Rsq_FULL[0.09,0.5]\',\'MR_fR1[300.,800.]\',\'Rsq_fR1[0.09,0.2]\',\'MR_fR2[300.,650.]\',\'Rsq_fR2[0.2,0.3]\',\'MR_fR3[300.,450.]\',\'Rsq_fR3[0.30,0.45]\',\'MR_fR4[300.,400.]\',\'Rsq_fR4[0.45,0.50]\',\'MR_sR1[800.,3500]\',\'Rsq_sR1[0.09,0.2]\',\'MR_sR2[650.,3500]\',\'Rsq_sR2[0.2,0.3]\',\'MR_sR3[450.,3500]\',\'Rsq_sR3[0.30,0.45]\',\'MR_sR4[400.,3500]\',\'Rsq_sR4[0.45,0.50]\']')
            
#config.write(outfile)
#outfile.close()
rootfile.Close()




