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

BoxName = ["Had", "Mu", "Ele", "MuMu", "MuEle", "EleEle"]
#for Box in BoxName:
#  
#    boxDir = rootfile.Get(Box)
#    if boxDir is None or not boxDir or not boxDir.InheritsFrom('TDirectory'):
#        continue    
#    fitresult = rootfile.Get(Box+"/fitresult_fitmodel_RMRTree")
#    print Box
#    fitresult.Print("V")
print "Combined"   
#fitresult = rootfile.Get("Combined_Mu_Ele_dir/fitresult_fitmodel_sim_MergedDataSet")
fitresult = rootfile.Get("RazorMultiBoxSim_dir/fitresult_fitmodel_sim_MergedDataSet")
fitresult.Print("V")
rootfile.Close()
