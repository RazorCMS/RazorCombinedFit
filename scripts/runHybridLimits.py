#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys
import time
from array import *

def getXsecRange(box,neutralinopoint,gluinopoint):
    lumi = 19300
    name = "T1bbbb"
    label = "MR400.0_R0.5"
    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)

    mDelta = (gluinopoint*gluinopoint - neutralinopoint*neutralinopoint)/gluinopoint
    print "mDelta = %f"%mDelta
    if mDelta < 800:
        xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
    else:
        xsecRange = [0.0005, 0.001, 0.005, 0.01, 0.05]
        

    return xsecRange

    
def writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint,hypo,t):
    nToys = 125 # toys per command
                # actually run command twice to get 250 toys
    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
    # prepare the script to run
    xsecstring = str(xsecpoint).replace(".","p")
    outputname = submitDir+"/submit_"+massPoint+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".src"
    outputfile = open(outputname,'w')
    
    tagHypo = ""
    if hypo == "B":
        tagHypo = "-e"
        
    ffDir = outputDir+"/logs_"+massPoint+"_"+xsecstring+"_"+hypo
    outputfile.write('#!/usr/bin/env bash -x\n')
    outputfile.write("export WD=/tmp/${USER}/Razor2012_%s_%s_%s_%i\n"%(massPoint,box,xsecstring,t))
    outputfile.write("mkdir -p $WD\n")
    outputfile.write("cd $WD\n")
    outputfile.write("scramv1 project CMSSW CMSSW_6_1_1\n")
    outputfile.write("cd CMSSW_6_1_1/src\n")
    outputfile.write("eval `scramv1 run -sh`\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/external/gcc/4.3.2/x86_64-slc5/setup.sh\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.34.05/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh\n")
    outputfile.write("export CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW\n")
    outputfile.write("cvs co -d RazorCombinedFit UserCode/wreece/RazorCombinedFit\n")
    outputfile.write("cd RazorCombinedFit\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("make\n")
    
    outputfile.write("export NAME=\"T1bbbb\"\n")
    outputfile.write("export LABEL=\"MR400.0_R0.5\"\n")
    
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/FullFits2012ABCD.root $PWD\n")
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/${NAME}_%s_${LABEL}*.root $PWD\n"%massPoint)
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/NuisanceTree.root $PWD\n")

    nToyOffset = nToys*(2*t)
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_hybrid.config -i FullFits2012ABCD.root -l --nuisance-file NuisanceTree.root --nosave-workspace ${NAME}_%s_${LABEL}_%s.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i\n"%(massPoint,box,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
    nToyOffset = nToys*(2*t+1)
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_hybrid.config -i FullFits2012ABCD.root -l --nuisance-file NuisanceTree.root --nosave-workspace ${NAME}_%s_${LABEL}_%s.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i\n"%(massPoint,box,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    outputfile.write("cp $WD/CMSSW_6_1_1/src/RazorCombinedFit/*.root $HOME/work/RAZORLIMITS/Hybrid/\n")
    outputfile.write("rm -rf $WD\n")
    
    outputfile.close

    return outputname,ffDir
if __name__ == '__main__':
    box = sys.argv[1]
    nJobs = 12 # do 250=125+125 toys each job => 3000 toys
    
    print box

    gchipairs = [(1125, 100), (1225, 100), (1325, 100),
                 (1125, 200), (1225, 200), (1325, 200), (1375, 200),
                 (1125, 300), (1225, 300), (1325, 300), (1375, 300),
                 (1125, 400), (1225, 400), (1325, 400), (1375, 400),
                 (1125, 500), (1225, 500), (1325, 500), (1375, 500),
                 ( 825, 600), ( 925, 600), (1025, 600), (1125, 600), (1225, 600), (1325, 600), (1375, 600),
                 ( 825, 700), ( 925, 700), (1025, 700), (1125, 700), (1225, 700), (1325, 700), (1375, 700),
                 ( 825, 800), ( 925, 800), (1025, 800), (1125, 800), (1225, 800), (1325, 800), (1375, 800)]

    #gchipairs = [(1225,0)]
    
    queue = "8nh"
    
    pwd = os.environ['PWD']
    
    submitDir = "submit"
    outputDir = "output"+box
    
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(outputDir))

    hypotheses = ["B","SpB"]

    for gluinopoint, neutralinopoint in gchipairs:
        xsecRange = getXsecRange(box,neutralinopoint,gluinopoint)
        for xsecpoint in xsecRange:
            for hypo in hypotheses:
                for t in xrange(0,nJobs):
                    print "Now scanning xsec = %f"%xsecpoint
                    outputname,ffDir = writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint,hypo,t)
                    os.system("mkdir -p %s/%s"%(pwd,ffDir))
                    time.sleep(3)
                    os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    #os.system("source "+pwd+"/"+outputname)
                        
