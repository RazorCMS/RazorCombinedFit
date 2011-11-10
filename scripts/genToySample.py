#! /usr/bin/env python
import ConfigParser
import os
import sys
import ROOT as rt
from RazorCombinedFit.Framework import Box
import RootTools

minMR = float(sys.argv[1])
maxMR = float(sys.argv[2])
minRsq = float(sys.argv[3])
maxRsq = float(sys.argv[4])
myfile = rt.TFile.Open(sys.argv[5])
mydata = myfile.Get("RMRTree")
mytree = mydata.tree()
#make histogram to compute number of entries
myTH2 = rt.TH2D("h", "h", 100, minMR, maxMR, 100, minRsq, maxRsq)
mytree.Project("h", "Rsq:MR", "W")
Nev = myTH2.Integral()
print Nev
print mytree.GetEntries()
# create roohistPDF
MR = rt.RooRealVar("MR", "MR", minMR, maxMR)
Rsq = rt.RooRealVar("Rsq", "Rsq", minRsq, maxRsq)
W = rt.RooRealVar("W", "W", 0, 100000000.)
#new dataset with weight
wdata = rt.RooDataSet('RMRTree','Weighted Cocktail', mydata.get(),"W")
wdata.append(mydata)
myhistdata = rt.RooDataHist("hdata", "hdata", rt.RooArgSet(MR, Rsq), wdata)
mypdf = rt.RooHistPdf("pdf", "pdf", rt.RooArgSet(MR, Rsq), myhistdata)
myNewData = mypdf.generate(rt.RooArgSet(MR, Rsq), int(Nev))
myNewData.SetName("RMRTree")
myOutfile = rt.TFile.Open(sys.argv[6], "recreate")
myNewData.Write()
myOutfile.Close()
myfile.Close()
