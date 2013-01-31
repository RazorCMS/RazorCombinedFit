#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys
from array import *
import pickle

if __name__ == '__main__':
    box = sys.argv[1]

    def loadNorms():
        pkl = "/afs/cern.ch/user/w/wreece/public/Razor2012/SMS-T2tt_FineBin_Mstop-225to1200_mLSP-0to1000_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-PAT_CMG_V5_6_0_B.pkl"
        return pickle.load(file(pkl))

    def select_point(point):
        return (int(point[0]) % 50 == 0 and int(point[1]) in [0,100])
   
    queue = "2nd"
    pwd = os.environ['PWD']
    submitDir = "submit"
    outputDir = "output"+box
    
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(outputDir))
#    for i in range(0,2) :
    norms = loadNorms()
    for point in norms.iterkeys():
        if not select_point(point): continue
        #massPoint = "%s.0_0.0"%(200+i*50)
        massPoint = "%s_%s"%(point[0], point[1])
        # prepare the script to run
        outputname = submitDir+"/submit_"+massPoint+"_"+box+".src"
        outputfile = open(outputname,'w')
        outputfile.write('#!/bin/bash\n')
        outputfile.write('cd %s \n'%pwd)
        outputfile.write('echo $PWD \n')
        outputfile.write('eval `scramv1 runtime -sh` \n')
        ffDir = outputDir+"/logs_"+massPoint
        outputfile.write("mkdir -p %s \n"%(ffDir));
        outputfile.write('sh macros/multijet/runPoint.sh "%s" %s'%(massPoint, box))
        
        outputfile.close
        os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log.log source "+pwd+"/"+outputname)
#        os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log.log source "+pwd+"/"+outputname)

