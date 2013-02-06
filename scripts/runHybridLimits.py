#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys
import time
from array import *
def getUpperXsec(box,neutralinopoint,gluinopoint):
    lumi = 19300
    name = "T1bbbb"
    label = "MR400.0_R0.5"
    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
    signalFile = rt.TFile("/afs/cern.ch/user/w/woodson/public/Razor2013/Signal/"+name+"_"+massPoint+"_"+label+"_"+box+".root")
    wHisto = signalFile.Get("wHisto")
    mrMean = wHisto.GetMean(1)
    stop_xs = 0.0
    yield_at_xs = [(stop_xs,0.0)]
    #with 15 signal events, we *should* be able to set a limit
    print "signal mrMean = %f"%mrMean
    if mrMean < 800:
        eventsToExclude = 150
        poi_max = 1.
    elif mrMean < 1000:
        eventsToExclude = 100
        poi_max = 0.5
    elif mrMean < 1600:
        eventsToExclude = 50
        poi_max = 0.2
    else:
        eventsToExclude = 25
        poi_max = 0.05
        
    # while yield_at_xs[-1][0] < eventsToExclude:
    #     stop_xs += 1e-4
    #     signal_yield = stop_xs*(wHisto.Integral())*lumi
    #     yield_at_xs.append( (signal_yield, stop_xs) )
    # poi_max = yield_at_xs[-1][1]
    # print 'Estimated POI Max:',poi_max

    return poi_max

    
def writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint,hypo,t):
    
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
    outputfile.write("scramv1 project CMSSW CMSSW_5_3_7_patch4\n")
    outputfile.write("cd CMSSW_5_3_7_patch4/src\n")
    outputfile.write("eval `scramv1 run -sh`\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.32.02/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh\n")
    
    outputfile.write("export CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW\n")
    outputfile.write("cvs co -d RazorCombinedFit UserCode/wreece/RazorCombinedFit\n")
    outputfile.write("cd RazorCombinedFit\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("make\n")
    
    outputfile.write("export NAME=\"T1bbbb\"\n")
    outputfile.write("export LABEL=\"MR400.0_R0.5\"\n")
    
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/SidebandFits2012ABCD.root $PWD\n")
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/${NAME}_%s_${LABEL}*.root $PWD\n"%massPoint)
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_hybrid.config -i SidebandFits2012ABCD.root -l --nosave-workspace ${NAME}_%s_${LABEL}_%s.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i.root %s --xsec %f -t 1000\n"%(massPoint,box,massPoint,box,xsecstring,hypo,t,tagHypo,xsecpoint))

    outputfile.write("cp $WD/CMSSW_5_3_7_patch4/src/RazorCombinedFit/*.root $HOME/work/RAZORLIMITS/Hybrid/\n")
    outputfile.write("rm -rf $WD\n")
    
    outputfile.close

    return outputname,ffDir
if __name__ == '__main__':
    box = sys.argv[1]
    nJobs = 3 # do 1000 toys each job
    
    print box
    
    gluinopoints = range(425,2025,200)
    #dsneutralinopoints = [0, 100]
    #gluinopoints = [1325]
    neutralinopoints = [0]
    queue = "1nd"
    
    pwd = os.environ['PWD']
    
    submitDir = "submit"
    outputDir = "output"+box
    
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(outputDir))

    xsecsteps = [0.01,0.05,0.1,0.5,1.0]
    hypotheses = ["B","SpB"]

    for neutralinopoint in neutralinopoints:
        for gluinopoint in gluinopoints:
            for xsecstep in xsecsteps:
                for hypo in hypotheses:
                    for t in xrange(0,nJobs):
                        poi_max = getUpperXsec(box,neutralinopoint,gluinopoint)
                        xsecunrounded = xsecstep*poi_max
                        xsecpoint = float("%.4f"%(xsecunrounded))
                        print "Now scanning xsec = %f"%xsecpoint
                        
                        outputname,ffDir = writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint,hypo,t)
                        os.system("mkdir -p %s/%s"%(pwd,ffDir))
                        time.sleep(3)
                        os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                        os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                        
