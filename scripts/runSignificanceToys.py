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
        gchipairs = [(150, 25), (150, 50),
                     (175, 25), (175, 50), (175, 75),
                     (200, 25), (200, 50), (200, 75), (200, 100),
                     (225, 25), (225, 50), (225, 75), (225, 100), (225, 125),
                     (250, 25), (250, 50), (250, 75), (250, 100), (250, 125), (250, 150),
                     (275, 25), (275, 50), (275, 75), (275, 100), (275, 125), (275, 150), (275, 175),
                     (300, 25), (300, 50), (300, 75), (300, 100), (300, 125), (300, 150), (300, 175), (300, 200),
                     (325, 25), (325, 50), (325, 75), (325, 100), (325, 125), (325, 150), (325, 175), (325, 200), (325, 225),
                     (350, 25), (350, 50), (350, 75), (350, 100), (350, 125), (350, 150), (350, 175), (350, 200), (350, 225), (350, 250),
                     (375, 25), (375, 50), (375, 75), (375, 100), (375, 125), (375, 150), (375, 175), (375, 200), (375, 225), (375, 250), (375, 275),
                     (400, 25), (400, 50), (400, 75), (400, 100), (400, 125), (400, 150), (400, 175), (400, 200), (400, 225), (400, 250), (400, 275), (400, 300),
                     (425, 25), (425, 50), (425, 75), (425, 100), (425, 125), (425, 150), (425, 175), (425, 200), (425, 225), (425, 250), (425, 275), (425, 300), (425, 325),
                     (450, 25), (450, 50), (450, 75), (450, 100), (450, 125), (450, 150), (450, 175), (450, 200), (450, 225), (450, 250), (450, 275), (450, 300), (450, 325), (450, 350),
                     (475, 25), (475, 50), (475, 75), (475, 100), (475, 125), (475, 150), (475, 175), (475, 200), (475, 225), (475, 250), (475, 275), (475, 300), (475, 325), (475, 350), (475, 375),
                     (500, 25), (500, 50), (500, 75), (500, 100), (500, 125), (500, 150), (500, 175), (500, 200), (500, 225), (500, 250), (500, 275), (500, 300), (500, 325), (500, 350), (500, 375), (500, 400),
                     (525, 25), (525, 50), (525, 75), (525, 100), (525, 125), (525, 150), (525, 175), (525, 200), (525, 225), (525, 250), (525, 275), (525, 300), (525, 325), (525, 350), (525, 375), (525, 400), (525, 425),
                     (550, 25), (550, 50), (550, 75), (550, 100), (550, 125), (550, 150), (550, 175), (550, 200), (550, 225), (550, 250), (550, 275), (550, 300), (550, 325), (550, 350), (550, 375), (550, 400), (550, 425), (550, 450),
                     (575, 25), (575, 50), (575, 75), (575, 100), (575, 125), (575, 150), (575, 175), (575, 200), (575, 225), (575, 250), (575, 275), (575, 300), (575, 325), (575, 350), (575, 375), (575, 400), (575, 425), (575, 450), (575, 475),
                     (600, 25), (600, 50), (600, 75), (600, 100), (600, 125), (600, 150), (600, 175), (600, 200), (600, 225), (600, 250), (600, 275), (600, 300), (600, 325), (600, 350), (600, 375), (600, 400), (600, 425), (600, 450), (600, 475), (600, 500),
                     (625, 25), (625, 50), (625, 75), (625, 100), (625, 125), (625, 150), (625, 175), (625, 200), (625, 225), (625, 250), (625, 275), (625, 300), (625, 325), (625, 350), (625, 375), (625, 400), (625, 425), (625, 450), (625, 475), (625, 500), (625, 525),
                     (650, 25), (650, 50), (650, 75), (650, 100), (650, 125), (650, 150), (650, 175), (650, 200), (650, 225), (650, 250), (650, 275), (650, 300), (650, 325), (650, 350), (650, 375), (650, 400), (650, 425), (650, 450), (650, 475), (650, 500), (650, 525), (650, 550),
                     (675, 25), (675, 50), (675, 75), (675, 100), (675, 125), (675, 150), (675, 175), (675, 200), (675, 225), (675, 250), (675, 275), (675, 300), (675, 325), (675, 350), (675, 375), (675, 400), (675, 425), (675, 450), (675, 475), (675, 500), (675, 525), (675, 550), (675, 575),
                     (700, 25), (700, 50), (700, 75), (700, 100), (700, 125), (700, 150), (700, 175), (700, 200), (700, 225), (700, 250), (700, 275), (700, 300), (700, 325), (700, 350), (700, 375), (700, 400), (700, 425), (700, 450), (700, 475), (700, 500), (700, 525), (700, 550), (700, 575), (700, 600),
                     (725, 25), (725, 50), (725, 75), (725, 100), (725, 125), (725, 150), (725, 175), (725, 200), (725, 225), (725, 250), (725, 275), (725, 300), (725, 325), (725, 350), (725, 375), (725, 400), (725, 425), (725, 450), (725, 475), (725, 500), (725, 525), (725, 550), (725, 575), (725, 600), (725, 625),
                     (750, 25), (750, 50), (750, 75), (750, 100), (750, 125), (750, 150), (750, 175), (750, 200), (750, 225), (750, 250), (750, 275), (750, 300), (750, 325), (750, 350), (750, 375), (750, 400), (750, 425), (750, 450), (750, 475), (750, 500), (750, 525), (750, 550), (750, 575), (750, 600), (750, 625), (750, 650),
                     (775, 25), (775, 50), (775, 75), (775, 100), (775, 125), (775, 150), (775, 175), (775, 200), (775, 225), (775, 250), (775, 275), (775, 300), (775, 325), (775, 350), (775, 375), (775, 400), (775, 425), (775, 450), (775, 475), (775, 500), (775, 525), (775, 550), (775, 575), (775, 600), (775, 625), (775, 650), (775, 675),
                     (800, 25), (800, 50), (800, 75), (800, 100), (800, 125), (800, 150), (800, 175), (800, 200), (800, 225), (800, 250), (800, 275), (800, 300), (800, 325), (800, 350), (800, 375), (800, 400), (800, 425), (800, 450), (800, 475), (800, 500), (800, 525), (800, 550), (800, 575), (800, 600), (800, 625), (800, 650), (800, 675), (800, 700)]
        
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
        srcDict[i] = ["0-0"]
        
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
