#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys
from array import *
import time
import glob

def writeBashScript(box,sideband,fitmode,nToy,njets,point, datasetName):
    pwd = os.environ['PWD']
            
    submitDir = "submit"
    resultDir = "/afs/cern.ch/work/l/lucieg/private/toys10k_%s_%s_%s_%s/%s_%s/toy_%s/"%(njets,datasetName,fitmode,point,sideband,box,str(nToy))
    resultDirold= "/afs/cern.ch/work/l/lucieg/private/toys10k_%s_%s_%s_%s/%s_%s"%(njets,datasetName,fitmode,point,sideband,box)
    tagFR = "--fit-region="+sideband
    tag3D = "--"+fitmode

    if sideband == "FULL":
        fitregion = "FULL"
    else :
        fitregion = "LowRsq,LowMR"
    
    tagPrintPlots = "--printPlots"
        
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(resultDir))
    # prepare the script to run
    outputname = submitDir+"/submit_"+njets+'_'+datasetName+"_"+fitmode+"_"+sideband+"_"+box+"_"+str(nToy)+'_'+point+".src"
    outputfile = open(outputname,'w')
    outputfile.write('#!/bin/bash\n')
    outputfile.write('cd %s \n'%pwd)
    outputfile.write('echo $PWD \n')
    outputfile.write('eval `scramv1 runtime -sh` \n')
    outputfile.write("source setup.sh\n")
    outputfile.write("python /afs/cern.ch/user/l/lucieg/scratch1/Oct18/CMSSW_6_2_0/src/RazorCombinedFit/scripts/makeToyPVALUE_sigbin.py %s %s/expected_sigbin_%s.root %s %s %s %s %s -b \n"%(box, resultDirold+"_FF", box, resultDirold+"/frtoydata_"+box+"_"+str(nToy)+".root", resultDir,tagFR,tag3D,tagPrintPlots))
           
            
    outputfile.close

    return outputname, resultDir, pwd

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "\nRun the script as follows:\n"
        print "python scripts/runToys DatasetName BoxName FitRegion"
        print "with:"
        print " DatasetName = name of the sample (TTJets, WJets, SMCocktail, MuHad-Run2012ABCD, ElectronHad-Run2012ABCD, etc)"
        print " BoxName = name of the Box (MuMu, MuEle, etc, or All)"
        print " FitRegion = name of the fit region (FULL, Sideband, or All)"
        print ""
        print "After the inputs you can specify the following options"
        print "--q=queue"
        print "--t=number of toys"
        sys.exit()
    
    datasetName = sys.argv[1]
    box = sys.argv[2]
    sideband = sys.argv[3]
    fitmode = sys.argv[4]
    #fitmode = '3D'
    queue = "8nh"
    nToys = 10000
    njets = 'gt4jets'
   
    point  = ''
    
    
    for i in range(4,len(sys.argv)):
        if sys.argv[i].find("--q=") != -1:
            queue = sys.argv[i].replace("--q=","")
        if sys.argv[i].find("--t=") != -1:
            nToys = int(sys.argv[i].replace("--t=",""))
      
    boxNames = [sys.argv[2]]

    if sys.argv[3]=='All':
        sidebandNames = ['Sideband','FULL']
    else:
        sidebandNames = [sys.argv[3]]
    

    for box in boxNames:
        for sideband in sidebandNames:
            resultDir = "/afs/cern.ch/work/l/lucieg/private/toys10k_%s_%s_%s%s"%(njets,datasetName,fitmode,point)
            for i in range(1214, nToys, 1):
                outputname,ffDir,pwd = writeBashScript(box,sideband,fitmode,i,njets, point,datasetName)
                os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(i)+".log source "+pwd+"/"+outputname)
                os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(i)+".log source "+pwd+"/"+outputname)
                    
                
   
