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
from getGChiPairs import *

    
def writeBashScript(box,model,submitDir,neutralinopoint,gluinopoint,xsecpoint,lumi,fitRegion,hypo,t):
    nToys = 125 # toys per command
    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
    # prepare the script to run
    xsecstring = str(xsecpoint).replace(".","p")
    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_"+fitRegion+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".src"
    outputfile = open(outputname,'w')

    label = "MR300.0_R0.387298334621"
    
    tagHypo = ""
    if hypo == "B":
        tagHypo = "-e"
        
    ffDir = outputDir+"/logs_"+model+"_"+massPoint+"_"+xsecstring+"_"+hypo
    user = os.environ['USER']
    
    combineDir = "/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/Combine/"%(user[0],user)
    
    outputfile.write('#!/usr/bin/env bash -x\n')
    outputfile.write('echo $SHELL\n')
    outputfile.write('pwd\n')
    outputfile.write('cd /afs/cern.ch/work/w/woodson/RAZORDMLIMITS/CMSSW_6_1_1/src/RazorCombinedFit \n')
    outputfile.write('pwd\n')
    outputfile.write("export SCRAM_ARCH=slc5_amd64_gcc472\n")
    outputfile.write('eval `scramv1 runtime -sh`\n')
    outputfile.write('source setup.sh\n')
    outputfile.write("export TWD=${PWD}/Razor2013_%s_%s_%s_%s_%i\n"%(model,massPoint,box,xsecstring,t))
    outputfile.write("mkdir -p $TWD\n")
    outputfile.write("cd $TWD\n")
    outputfile.write('pwd\n')
    
    #outputfile.write("export SCRAM_ARCH=slc5_amd64_gcc472\n")
    #outputfile.write("scramv1 project CMSSW_6_1_1\n")
    #outputfile.write("cd CMSSW_6_1_1/src\n")
    #outputfile.write('pwd\n')
    #outputfile.write("eval `scramv1 runtime -sh`\n")
    #outputfile.write("root -l -q\n")
    #outputfile.write("git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit\n")
    #outputfile.write("cd HiggsAnalysis/CombinedLimit\n")
    #outputfile.write('pwd\n')
    #outputfile.write("git pull origin master\n")
    #outputfile.write("git checkout V03-05-00\n")
    #outputfile.write("scramv1 b\n")
    #outputfile.write("export WD=${TWD}/CMSSW_6_1_1/src\n")
    #outputfile.write("cd $WD\n")
    #outputfile.write('pwd\n')
    #outputfile.write("git clone git@github.com:RazorCMS/RazorCombinedFit.git\n")
    #outputfile.write("cd RazorCombinedFit\n")
    #outputfile.write('pwd\n')
    #outputfile.write("mkdir -p lib\n")
    #outputfile.write("source setup.sh\n")
    #outputfile.write("make clean; make -j 4\n")
    
    outputfile.write("export NAME=\"%s\"\n"%model)
    outputfile.write("export LABEL=\"%s\"\n"%label)
    
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/FULLFits2012ABCD_21Nov2013.root $PWD\n")
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/SidebandFits2012ABCD_21Nov2013.root $PWD\n")
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/${NAME}/${NAME}_%s_${LABEL}*.root $PWD\n"%massPoint)
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/NuisanceTreeISR.root $PWD\n")
        
    #outputfile.write("python scripts/prepareCombine.py %s ${NAME} FULLFits2012ABCD.root ${NAME}_%s_${LABEL}_%s.root\n"%(box,massPoint,box))
    #outputfile.write("combine -M Asymptotic -n ${NAME}_%s_%s razor_combine_%s_${NAME}.txt\n"%(massPoint,box,box))

    boxes =  box.split("_")
    for ibox in boxes:
        outputfile.write("python /afs/cern.ch/work/w/woodson/RAZORDMLIMITS/CMSSW_6_1_1/src/RazorCombinedFit/scripts/prepareCombine.py --box %s --model ${NAME} -i %sFits2012ABCD_21Nov2013.root ${NAME}_%s_${LABEL}_%s.root -c /afs/cern.ch/work/w/woodson/RAZORDMLIMITS/CMSSW_6_1_1/src/RazorCombinedFit/config_summer2012/RazorInclusive2012_3D_hybrid.config --xsec %f --lumi %f --fit-region %s\n"%(ibox,fitRegion,massPoint,ibox,xsecpoint,lumi,fitRegion))
        outputfile.write("/afs/cern.ch/work/w/woodson/RAZORDMLIMITS/CMSSW_6_1_1/bin/slc5_amd64_gcc472/combine -M Asymptotic -n ${NAME}_%s_%s_%s razor_combine_%s_${NAME}.txt\n"%(massPoint,fitRegion,ibox,ibox))

    if len(boxes)>1:
        options = ["%s=razor_combine_%s_%s.txt"%(ibox,ibox,model) for ibox in boxes]
        option = " ".join(options)
        outputfile.write("/afs/cern.ch/work/w/woodson/RAZORDMLIMITS/CMSSW_6_1_1/bin/slc5_amd64_gcc472/combineCards.py %s > razor_combine_%s_%s.txt \n"%(option,box,model))
        outputfile.write("/afs/cern.ch/work/w/woodson/RAZORDMLIMITS/CMSSW_6_1_1/bin/slc5_amd64_gcc472/combine -M Asymptotic -n ${NAME}_%s_%s_%s razor_combine_%s_${NAME}.txt\n"%(massPoint,fitRegion,box,box))
        
    #outputfile.write("cp $WD/RazorCombinedFit/*.root %s \n"%combineDir)
    outputfile.write("cp $TWD/*.root %s \n"%combineDir)
    outputfile.write("cd; pwd; rm -rf $TWD\n")
    
    outputfile.close

    return outputname,ffDir

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "\nRun the script as follows:\n"
        print "python scripts/runCombineLimits.py Box Model Queue CompletedOutputTextFile"
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
    refXsec = 100.
    lumi = 19.3
    fitRegion="FULL"
    for i in xrange(5,len(sys.argv)):
        if sys.argv[i].find("--t3")!=-1: t3 = True
        if sys.argv[i].find("--mchi-lt")!=-1: mchi_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mchi-geq")!=-1: mchi_lower = float(sys.argv[i+1])
        if sys.argv[i].find("--mg-lt")!=-1: mg_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mg-geq")!=-1: mg_lower = float(sys.argv[i+1])
        if sys.argv[i].find("--xsec")!=-1: refXsec = float(sys.argv[i+1])
        if sys.argv[i].find("--lumi")!=-1: lumi = float(sys.argv[i+1])
        if sys.argv[i].find("--fit-region")!=-1: fitRegion = sys.argv[i+1]
    
    nJobs = 1 # do 1 toy each job => 1 toy
    
    print box, model, queue

    gchipairs = getGChiPairs(model)

    gchipairs = reversed(gchipairs)
    
    pwd = os.environ['PWD']
    
    submitDir = "submit"
    outputDir = "output"+fitRegion+box
    
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(outputDir))

    hypotheses = ["SpB"]

    # for compting what jobs are left:
    doneFile = open(done)
    outFileList = [outFile.replace("higgsCombine","").replace(".root\n","") for outFile in doneFile.readlines()]

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
        xsecRange = [refXsec]
        for xsecpoint in xsecRange:
            print "Now scanning mg = %.0f, mchi = %.0f, xsec = %.4f"%(gluinopoint, neutralinopoint,xsecpoint)
            for hypo in hypotheses:
                for t in xrange(0,nJobs):
                    xsecstring = str(xsecpoint).replace(".","p")
                    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
                    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_"+fitRegion+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".src"
                    output0 = str(outputname.replace("submit/submit_","").replace("xsec",""))
                    for i in xrange(0,nJobs):
                        output0 = output0.replace("SpB_%i.src"%i,"SpB_%s"%srcDict[i][0])
                    runJob = False
                    if output0 not in outFileList: 
                        missingFiles+=1
                        runJob = True
                    if not runJob: continue
                    outputname,ffDir = writeBashScript(box,model,submitDir,neutralinopoint,gluinopoint,xsecpoint,lumi,fitRegion,hypo,t)
                    os.system("mkdir -p %s/%s"%(pwd,ffDir))
                    totalJobs+=1
                    time.sleep(3)
                    os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
    print "Missing files = ", missingFiles
    print "Total jobs = ", totalJobs
