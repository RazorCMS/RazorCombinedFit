import ROOT as rt
import sys
import RootTools
import glob
from math import *
import os
from array import *


def testWorkspace(w):
    w.Print()

if __name__ == '__main__':
    rt.gSystem.Load("/afs/cern.ch/user/w/woodson/work/RAZORDMLIMITS/CMSSW_6_1_1/lib/slc5_amd64_gcc472/libHiggsAnalysisCombinedLimit.so")
    
    workspaceFile = rt.TFile.Open(sys.argv[1])
   
    testWorksapce(w)
