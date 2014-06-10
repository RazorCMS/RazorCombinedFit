#! /usr/bin/env python
from optparse import OptionParser

import os.path
import sys, re
from array import *

if __name__ == '__main__':
  
    queue = "1nd"
    pwd = os.environ['PWD']
    
    for LSPmass in range(25,700,25):

        submitDir = pwd+"/submit_"+str(LSPmass)
        resultDir = "/afs/cern.ch/work/l/lucieg/private/MC/T2ttMugt4jets/mLSP%s/"%(LSPmass)
        ffDir     = "/afs/cern.ch/work/l/lucieg/private/MC/T2ttMugt4jets/logs_%s"%(LSPmass)
    
        os.system("mkdir -p %s"%(submitDir)) 
        os.system("mkdir -p %s"%(ffDir))
        os.system("mkdir -p %s"%resultDir)
        # prepare the script to run
        for mass in range(150,  825, 25):
            print mass
            outputname = submitDir+"/submit_"+str(mass)+".src"
            outputfile = open(outputname,'w')
            outputfile.write('#!/bin/bash\n')
            outputfile.write('cd %s \n'%pwd)
            outputfile.write('echo $PWD \n')
            outputfile.write('eval `scramv1 runtime -sh` \n')
            outputfile.write("python Will2DatasetwithSYS.py -c /afs/cern.ch/user/l/lucieg/scratch1/Oct18/CMSSW_6_2_0/src/RazorCombinedFit/config_summer2012/RazorMultiJet2013_3D_hybrid.config  /afs/cern.ch/work/l/lucieg/public/forRazorStop/SMS-T2tt_mStop-Combo_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY/SMS-T2tt_mStop-Combo_mLSP_%s.0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY.root --mstop %s --mlsp %s -d %s"%(LSPmass,mass,LSPmass, resultDir))
            
            outputfile.close()
            #        os.system("echo bsub -q "+queue+" -o "+ffDir+"/log"+str(index)+".log source "+outputname)
            os.system("bsub -q "+queue+" -o "+ffDir+"/log"+str(mass)+".log source "+outputname)
