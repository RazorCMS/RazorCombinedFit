#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys
import time
from array import *

if __name__ == '__main__':
    box = sys.argv[1]
    print box
    
    gluinopoints = range(1225,1625,200)
    neutralinopoints = [0, 100]
    queue = "1nd"

    #gluinopoints = range(225,2025,100)
    #neutralinopoints = [0, 100]
    #queue = "1nd"
    
    pwd = os.environ['PWD']
    
    submitDir = "submit"
    outputDir = "output"+box
    
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(outputDir))
    
    for neutralinopoint in neutralinopoints:
        for gluinopoint in gluinopoints:
            massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
            # prepare the script to run
            outputname = submitDir+"/submit_"+massPoint+"_"+box+".src"
            outputfile = open(outputname,'w')
            outputfile.write('#!/bin/bash\n')
            outputfile.write('cd %s\n'%pwd)
            outputfile.write('echo $PWD\n')
            outputfile.write('eval `scramv1 runtime -sh`\n')
            ffDir = outputDir+"/logs_"+massPoint
            outputfile.write("mkdir -p %s\n"%(ffDir))
            outputfile.write('sh macros/multijet/runPoint.sh "%s" %s'%(massPoint,box))
            
            outputfile.close
            os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log.log source "+pwd+"/"+outputname)
            time.sleep(2)
            os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log.log source "+pwd+"/"+outputname)

