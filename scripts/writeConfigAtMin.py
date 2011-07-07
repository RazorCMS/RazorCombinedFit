#! /usr/bin/env python
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

BoxName = ["MuMu", "MuEle", "Mu", "EleEle", "Ele", "Had"]
for Box in BoxName:
    
    boxDir = rootfile.Get(Box)
    if boxDir is None or not boxDir or not boxDir.InheritsFrom('TDirectory'):
        continue
    
    # write the Box header
    outfile.write("["+Box+"]\n")
    # write the variables
    outfile.write("variables:	[")
    # get the Workspace
    myws = rootfile.Get(Box+"/Box"+Box+"_workspace")
    MR = myws.var("MR")
    outfile.write("'MR["+str(MR.getMin())+","+str(MR.getMax())+"]',")
    R = myws.var("R")
    outfile.write("'R["+str(R.getMin())+","+str(R.getMax())+"]',")
    Rsq = myws.var("Rsq")
    outfile.write("'Rsq["+str(Rsq.getMin())+","+str(Rsq.getMax())+"]']\n")
    # write the pdf parameters
    fitresult = rootfile.Get(Box+"/fitresult_fitmodel_RMRTree")
    pdf1 =   "pdf1:           ["
    pdf2 =   "pdf2:           ["
    others = "others:         ["
    parlist = fitresult.floatParsFinal()
    for par in RootTools.RootIterator.RootIterator(parlist):
        if par.GetName().find("1st") != -1:      pdf1   += "'"+par.GetName()+'['+str(par.getVal())+','+str(par.getMin())+','+str(par.getMax())+"]',"
        elif par.GetName().find("2nd") != -1: pdf2   += "'"+par.GetName()+'['+str(par.getVal())+','+str(par.getMin())+','+str(par.getMax())+"]',"
        else:                                    others += "'"+par.GetName()+'['+str(par.getVal())+','+str(par.getMin())+','+str(par.getMax())+"]',"
        continue
    outfile.write(pdf1[:-1]+"]\n")
    outfile.write(pdf2[:-1]+"]\n")
    outfile.write(others[:-1]+"]\n\n")
    continue
outfile.close()
