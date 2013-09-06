#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys
import time
from math import *
from array import *

def getGChiPairs(model):
    if model=="T2tt":
        gchipairs = [(800, 25)]
    return gchipairs

def getXsecRange(model,neutralinoMass,gluinoMass):
    if model=="T2tt":
        xsecRange = [0.0]
    return sorted(list(set(xsecRange)))

    
def writeSgeScript(box,model,submitDir,neutralinopoint,gluinopoint,xsecpoint,hypo,t):
    nToys = 1 # toys per command
    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
    # prepare the script to run
    xsecstring = str(xsecpoint).replace(".","p")
    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".src"
    outputfile = open(outputname,'w')

    label = "MR300.0_R0.387298334621"
    
    tagHypo = ""
    if hypo == "B":
        tagHypo = "-e"
        
    ffDir = outputDir+"/logs_"+model+"_"+massPoint+"_"+xsecstring+"_"+hypo
    user = os.environ['USER']
    
    hybridDir = "/home/jduarte/work/RAZORLIMITS/Hybrid/"
    
    outputfile.write('#!/bin/sh\n')
    outputfile.write("export TWD=/tmp/${USER}/Razor2013_%s_%s_%s_%s_%i\n"%(model,massPoint,box,xsecstring,t))
    outputfile.write("mkdir -p /tmp/${USER}\n")
    outputfile.write("mkdir -p $TWD\n")
    outputfile.write("cd $TWD\n")
    outputfile.write("export SCRAM_ARCH=slc5_amd64_gcc472\n")
    outputfile.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
    outputfile.write("scram project CMSSW_6_2_0\n")
    outputfile.write("cd CMSSW_6_2_0/src\n")
    outputfile.write("eval `scram runtime -sh`\n")
    outputfile.write("export WD=/tmp/${USER}/Razor2013_%s_%s_%s_%s_%i/CMSSW_6_2_0/src\n"%(model,massPoint,box,xsecstring,t))
    outputfile.write("export GIT_SSL_NO_VERIFY=true\n")
    outputfile.write("export https_proxy=newman.ultralight.org:3128\n")
    outputfile.write("export http_proxy=newman.ultralight.org:3128\n")
    outputfile.write("export SSH_ASKPASS=\"\"\n")
    outputfile.write("git clone https://github.com/RazorCMS/RazorCombinedFit.git\n")
    outputfile.write("cd RazorCombinedFit\n")
    #outputfile.write("git checkout tags/woodson_300713\n")
    outputfile.write("mkdir -p lib\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("make clean; make -j 4\n")
    
    outputfile.write("export NAME=\"%s\"\n"%model)
    outputfile.write("export LABEL=\"%s\"\n"%label)
    
    outputfile.write("cp /home/jduarte/public/Razor2013/Background/FULLFits2012ABCD.root $PWD\n")
    outputfile.write("cp /home/jduarte/public/Razor2013/Signal/${NAME}/${NAME}_%s_${LABEL}*.root $PWD\n"%massPoint)
    outputfile.write("cp /home/jduarte/public/Razor2013/Signal/NuisanceTreePulls.root $PWD\n")
    outputfile.write("cp /home/jduarte/public/Razor2013/Signal/sig.config $PWD/config_summer2012/\n")
        
    nToyOffset = nToys*t
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/sig.config -i FULLFits2012ABCD.root -l --nuisance-file NuisanceTreePulls.root --nosave-workspace ${NAME}_%s_${LABEL}_%s.root -o Razor2013HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i --pulls -t %i\n"%(massPoint,box,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    outputfile.write("cp $WD/RazorCombinedFit/*.root %s \n"%hybridDir)
    outputfile.write("cd; rm -rf $TWD\n")
    
    outputfile.close
    
    return outputname,ffDir
    
def writeBashScript(box,model,submitDir,neutralinopoint,gluinopoint,xsecpoint,hypo,t):
    nToys = 1 # toys per command
    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
    # prepare the script to run
    xsecstring = str(xsecpoint).replace(".","p")
    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".src"
    outputfile = open(outputname,'w')

    label = "MR300.0_R0.387298334621"
    
    tagHypo = ""
    if hypo == "B":
        tagHypo = "-e"
        
    ffDir = outputDir+"/logs_"+model+"_"+massPoint+"_"+xsecstring+"_"+hypo
    user = os.environ['USER']
    
    hybridDir = "/afs/cern.ch/work/%s/%s/RAZORLIMITS/Hybrid/"%(user[0],user)
    
    outputfile.write('#!/usr/bin/env bash -x\n')
    outputfile.write("export TWD=/tmp/${USER}/Razor2013_%s_%s_%s_%s_%i\n"%(model,massPoint,box,xsecstring,t))
    outputfile.write("mkdir -p $TWD\n")
    outputfile.write("cd $TWD\n")
    outputfile.write("export SCRAM_ARCH=slc5_amd64_gcc472\n")
    outputfile.write("scram project CMSSW_6_2_0_pre8\n")
    outputfile.write("cd CMSSW_6_2_0_pre8/src\n")
    outputfile.write("eval `scram runtime -sh`\n")
    outputfile.write("export WD=/tmp/${USER}/Razor2013_%s_%s_%s_%s_%i/CMSSW_6_2_0_pre8/src\n"%(model,massPoint,box,xsecstring,t))
    outputfile.write("git clone git@github.com:RazorCMS/RazorCombinedFit.git\n")
    outputfile.write("cd RazorCombinedFit\n")
    #outputfile.write("git checkout tags/woodson_300713\n")
    outputfile.write("mkdir -p lib\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("make clean; make -j 4\n")
    
    outputfile.write("export NAME=\"%s\"\n"%model)
    outputfile.write("export LABEL=\"%s\"\n"%label)
    
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/FULLFits2012ABCD.root $PWD\n")
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/${NAME}/${NAME}_%s_${LABEL}*.root $PWD\n"%massPoint)
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/NuisanceTreePulls.root $PWD\n")
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/sig.config $PWD/config_summer2012/\n")
        
    nToyOffset = nToys*t
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/sig.config -i FULLFits2012ABCD.root -l --nuisance-file NuisanceTreePulls.root --nosave-workspace ${NAME}_%s_${LABEL}_%s.root -o Razor2013HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i --pulls -t %i\n"%(massPoint,box,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
    
    outputfile.write("cp $WD/RazorCombinedFit/*.root %s \n"%hybridDir)
    outputfile.write("cd; rm -rf $WD\n")
    
    outputfile.close

    return outputname,ffDir
if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "\nRun the script as follows:\n"
        print "python scripts/runHybridLimits.py Box Model Queue CompletedOutputTextFile"
        print "with:"
        print "- Box = name of the Box (MuMu, MuEle, etc.)"
        print "- Model = T1bbbb, T1tttt, T2tt, etc. "
        print "- Queue = 1nh, 8nh, 1nd, etc."
        print "- CompletedOutputTextFile = text file containing all completed output files"
        print ""
        sys.exit()
    box = sys.argv[1]
    model = sys.argv[2]
    queue = sys.argv[3]
    done  = sys.argv[4]
    t3 = False
    mchi_lower = 0
    mchi_upper = 2025
    mg_lower = 0
    mg_upper = 2025
    for i in xrange(5,len(sys.argv)):
        if sys.argv[i].find("--t3")!=-1: t3 = True
    for i in xrange(5,len(sys.argv)):
        if sys.argv[i].find("--mchi-lt")!=-1: mchi_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mchi-geq")!=-1: mchi_lower = float(sys.argv[i+1])
        if sys.argv[i].find("--mg-lt")!=-1: mg_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mg-geq")!=-1: mg_lower = float(sys.argv[i+1])
    
    nJobs = 1 # do 1 toy each job => 1 toy
    
    print box, model, queue

    gchipairs = getGChiPairs(model)

    gchipairs = reversed(gchipairs)
    
    pwd = os.environ['PWD']
    
    submitDir = "submit"
    outputDir = "output"+box
    
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(outputDir))

    hypotheses = ["SpB"]

    # for compting what jobs are left:
    doneFile = open(done)
    outFileList = [outFile.replace("Razor2013HybridLimit_","").replace(".root\n","") for outFile in doneFile.readlines()]

    # dictionary of src file to output file names
    nToys = 1 # toys per command
    srcDict = {}
    for i in xrange(0,nJobs):
        srcDict[i] = ["0-1"]
        
    totalJobs = 0
    missingFiles = 0
    for gluinopoint, neutralinopoint in gchipairs:
        if neutralinopoint < mchi_lower or neutralinopoint >= mchi_upper: continue
        if gluinopoint < mg_lower or gluinopoint >= mg_upper: continue
        xsecRange = getXsecRange(model,neutralinopoint,gluinopoint)
        for xsecpoint in xsecRange:
            print "Now scanning mg = %.0f, mchi = %.0f, xsec = %.4f"%(gluinopoint, neutralinopoint,xsecpoint)
            for hypo in hypotheses:
                for t in xrange(0,nJobs):
                    xsecstring = str(xsecpoint).replace(".","p")
                    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
                    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".src"
                    output0 = str(outputname.replace("submit/submit_","").replace("xsec",""))
                    for i in xrange(0,nJobs):
                        output0 = output0.replace("B_%i.src"%i,"B_%s"%srcDict[i][0])
                    runJob = False
                    if output0 not in outFileList: 
                        missingFiles+=1
                        runJob = True
                    if not runJob: continue
                    if t3:
                        outputname,ffDir = writeSgeScript(box,model,submitDir,neutralinopoint,gluinopoint,xsecpoint,hypo,t)
                        os.system("xfmkdir -p %s/%s"%(pwd,ffDir))
                        totalJobs+=1
                        time.sleep(3)
                        queuelist = ["all.q@compute-3-10.local","all.q@compute-3-11.local","all.q@compute-3-12.local",
                                     "all.q@compute-3-2.local","all.q@compute-3-3.local","all.q@compute-3-4.local",
                                     "all.q@compute-3-5.local","all.q@compute-3-7.local",
                                     "all.q@compute-3-9.local"]
                        queues = ",".join(queuelist)
                        
                        os.system("echo qsub -j y -q "+queues+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log "+pwd+"/"+outputname)
                        os.system("qsub -j y -q "+queues+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log "+pwd+"/"+outputname)
                        #os.system("source "+pwd+"/"+outputname)
                    else:    
                        outputname,ffDir = writeBashScript(box,model,submitDir,neutralinopoint,gluinopoint,xsecpoint,hypo,t)
                        os.system("mkdir -p %s/%s"%(pwd,ffDir))
                        totalJobs+=1
                        time.sleep(3)
                        os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                        os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                        #os.system("echo bsub -q "+queue+" -o /dev/null source "+pwd+"/"+outputname)
                        #os.system("bsub -q "+queue+" -o /dev/null source "+pwd+"/"+outputname)
                        #os.system("source "+pwd+"/"+outputname)
    print "Missing files = ", missingFiles
    print "Total jobs = ", totalJobs
