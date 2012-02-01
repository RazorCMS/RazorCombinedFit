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
boxNUM = int(sys.argv[5])
W = sys.argv[6]
myfile = rt.TFile.Open(sys.argv[7])
mytree = myfile.Get("EVENTS")
myTH2 = rt.TH2D("h", "h", 100, minMR, maxMR, 100, minRsq, maxRsq)
mytree.Project("h", "RSQ:MR", "%s*(BOX_NUM==%i)" %(W,boxNUM))
Nev = myTH2.Integral()
print Nev
print mytree.GetEntries()
# variables
MR = rt.RooRealVar("MR", "MR", minMR, maxMR)
Rsq = rt.RooRealVar("Rsq", "Rsq", minRsq, maxRsq)
a = rt.RooArgSet(MR,Rsq)
data = rt.RooDataSet('RMRTree','Selected R and MR',a)
for i in range(0,int(Nev)):
    myMR = rt.Double()
    myRsq = rt.Double()
    myTH2.GetRandom2(myMR,myRsq)
    a.setRealValue('MR',myMR)
    a.setRealValue('Rsq',myRsq)
    data.add(a)
#new dataset with weight
myOutfile = rt.TFile.Open(sys.argv[8], "recreate")
data.Write()
myTH2.Write()
myOutfile.Close()
myfile.Close()
