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

    
def writeBashScript(box,model,submitDir,neutralinoPoint,gluinoPoint,xsecPoint,fitRegion,signalRegion,t,nToys,significance,workspaceFlag,expected_a_priori):
    massPoint = "MG_%f_MCHI_%f"%(gluinoPoint, neutralinoPoint)
    workspaceString = ""
    if workspaceFlag:
        workspaceString = "Workspace"
    aprioriString = ""
    if expected_a_priori:
        aprioriString = "--expected-a-priori"
    
    # prepare the script to run
    xsecString = str(xsecPoint).replace(".","p")
    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_xsec"+xsecString+"_"+fitRegion+"_"+box+"_"+str(t)+".src"
    outputfile = open(outputname,'w')
    
    label = {"MuEle":"MR300.0_R0.387298334621","EleEle":"MR300.0_R0.387298334621","MuMu":"MR300.0_R0.387298334621",
             "EleJet":"MR300.0_R0.387298334621","EleMultiJet":"MR300.0_R0.387298334621","MuMultiJet":"MR300.0_R0.387298334621","MuJet":"MR300.0_R0.387298334621",
             "MultiJet":"MR400.0_R0.5","Jet2b":"MR400.0_R0.5"}
    
    sigma = {"MuEle":1.0,"EleEle":1.0,"MuMu":1.0,
             "EleJet":1.0,"EleMultiJet":1.0,"MuMultiJet":1.0,"MuJet":1.0,
             "MultiJet":1.0,"Jet2b":1.0}
        
    ffDir = outputDir+"/logs_"+model+"_"+massPoint+"_xsec"+xsecString+"_"+fitRegion+"_"+box
    user = os.environ['USER']
    
    combineDir = "/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/Combine/%s/"%(user[0],user,model)
    
    outputfile.write('#!/usr/bin/env bash -x\n')
    outputfile.write('mkdir -p %s\n'%combineDir)
    outputfile.write('echo $SHELL\n')
    outputfile.write('pwd\n')
    outputfile.write('cd /afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2/src/RazorCombinedFit \n'%(user[0],user))
    outputfile.write('pwd\n')
    outputfile.write("export SCRAM_ARCH=slc5_amd64_gcc472\n")
    outputfile.write("export CMSSW_BASE=/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2\n"%(user[0],user))
    outputfile.write('eval `scramv1 runtime -sh`\n')
    outputfile.write('source setup.sh\n')
    outputfile.write('cd - \n')
    outputfile.write("export TWD=${PWD}/Razor2013_%s_%s_%s_%s_%i\n"%(model,massPoint,box,xsecString,t))
    outputfile.write("mkdir -p $TWD\n")
    outputfile.write("cd $TWD\n")
    outputfile.write('pwd\n')
    
    outputfile.write("export NAME=\"%s\"\n"%model)
    boxes =  box.split("_")
    
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/FULLFits2012ABCD_2Nov2013.root $PWD\n")
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/SidebandFits2012ABCD_2Nov2013.root $PWD\n")
    for ibox in boxes:
        outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/${NAME}/${NAME}_%s_%s_%s.root $PWD\n"%(massPoint,label[ibox],ibox))
        outputfile.write("python /afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2/src/RazorCombinedFit/scripts/prepareCombine%s.py --box %s --model ${NAME} -i %sFits2012ABCD_2Nov2013.root ${NAME}_%s_%s_%s.root -c /afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2/src/RazorCombinedFit/config_summer2012/RazorInclusive2012_3D_combine.config --xsec %f --signal-region %s --sigma %f %s \n"%(user[0],user,workspaceString,ibox,fitRegion,massPoint,label[ibox],ibox,user[0],user,xsecPoint,signalRegion,sigma[ibox],aprioriString))
    if len(boxes)==1: 
        if significance and nToys<0:
            outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M ProfileLikelihood --significance -n ${NAME}_%s_xsec%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,massPoint,xsecString,fitRegion,ibox,t,ibox,massPoint))
        elif significance and nToys>0:
            outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --saveHybridResult --testStat PL --fork 4 -T %i --significance -n Signif${NAME}_%s_xsec%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,nToys,massPoint,xsecString,fitRegion,ibox,t,ibox,massPoint))
        elif nToys>0: 
            outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --saveHybridResult --testStat LHC -H Asymptotic --fork 4 -T %i -n ${NAME}_%s_xsec%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,nToys,massPoint,xsecString,fitRegion,ibox,t,ibox,massPoint))
        else:
            outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M Asymptotic --rRelAcc 0.0001 --picky --minimizerTolerance 0.0001 -n ${NAME}_%s_xsec%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,massPoint,xsecString,fitRegion,ibox,t,ibox,massPoint))
    elif len(boxes)>1:
        options = ["%s=razor_combine_%s_%s_%s.txt"%(ibox,ibox,model,massPoint) for ibox in boxes]
        option = " ".join(options)
        outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combineCards.py %s > razor_combine_%s_%s_%s.txt \n"%(user[0],user,option,box,model,massPoint))
        if significance and nToys<0:
            outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M ProfileLikelihood --significance -n ${NAME}_%s_xsec%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,massPoint,xsecString,fitRegion,box,t,box,massPoint))
        elif significance and nToys>0:
            outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --saveHybridResult --testStat PL --fork 4 -T %i --significance -n Signif${NAME}_%s_xsec%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,nToys,massPoint,xsecString,fitRegion,box,t,box,massPoint))
        elif nToys>0: 
            outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --saveHybridResult --testStat LHC -H Asymptotic --fork 4 -T %i -n ${NAME}_%s_xsec%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,nToys,massPoint,xsecString,fitRegion,box,t,box,massPoint))
        else:
            outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M Asymptotic -n ${NAME}_%s_xsec%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,massPoint,xsecString,fitRegion,box,t,box,massPoint))

    outputfile.write("cp $TWD/higgsCombine*.root %s \n"%combineDir)
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
    refXsecFile = None
    fitRegion="Sideband"
    signalRegion="FULL"
    significance = False
    workspaceFlag = True
    nToys = -1
    noSub = False
    expected_a_priori = False
    for i in xrange(5,len(sys.argv)):
        if sys.argv[i].find("--no-sub")!=-1: noSub = True
        if sys.argv[i].find("--t3")!=-1: t3 = True
        if sys.argv[i].find("--mchi-lt")!=-1: mchi_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mchi-geq")!=-1: mchi_lower = float(sys.argv[i+1])
        if sys.argv[i].find("--mg-lt")!=-1: mg_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mg-geq")!=-1: mg_lower = float(sys.argv[i+1])
        if sys.argv[i].find("--xsec")!=-1: 
            if sys.argv[i].find("--xsec-file")!=-1: 
                refXsecFile = sys.argv[i+1]
            else:
                refXsec = float(sys.argv[i+1])
        if sys.argv[i].find("--fit-region")!=-1: fitRegion = sys.argv[i+1]
        if sys.argv[i].find("--signal-region")!=-1: signalRegion = sys.argv[i+1]
        if sys.argv[i].find("--toys")!=-1: nToys = int(sys.argv[i+1])
        if sys.argv[i].find("--signif")!=-1: significance = True
        if sys.argv[i].find("--work")!=-1: workspaceFlag = True
        if sys.argv[i].find("--no-work")!=-1: workspaceFlag = False 
        if sys.argv[i].find("--expected-a-priori")!=-1: expected_a_priori = True
            
    if refXsecFile is not None:
        print "INFO: Input ref xsec file!"
        gluinoFile = rt.TFile.Open(refXsecFile,"READ")
        gluinoHistName = refXsecFile.split("/")[-1].split(".")[0]
        gluinoHist = gluinoFile.Get(gluinoHistName)
        
    nJobs = 1 # do 1 toy each job => 1 toy
    
    print box, model, queue

    gchipairs = getGChiPairs(model)

    gchipairs = reversed(gchipairs)
    
    pwd = os.environ['PWD']
    
    submitDir = "submit"+model+fitRegion+box
    outputDir = "output"+model+fitRegion+box
    
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(outputDir))

    # for compting what jobs are left:
    doneFile = open(done)
    if significance and nToys<0:
        outFileList = [outFile.replace("higgsCombine","").replace(".ProfileLikelihood.mH120.root\n","") for outFile in doneFile.readlines() if outFile.find("ProfileLikelihood")!=-1]
    elif significance and nToys>0:
        outFileList = [outFile.replace("higgsCombineSignif","").replace(".HybridNew.mH120.root\n","") for outFile in doneFile.readlines() if outFile.find("HybridNew")!=-1]
    elif nToys>0:
        outFileList = [outFile.replace("higgsCombine","").replace(".HybridNew.mH120.root\n","") for outFile in doneFile.readlines() if outFile.find("HybridNew")!=-1]
    else:
        outFileList = [outFile.replace("higgsCombine","").replace(".Asymptotic.mH120.root\n","") for outFile in doneFile.readlines() if outFile.find("Asymptotic")!=-1]
 
    totalJobs = 0
    missingFiles = 0
    for gluinoPoint, neutralinoPoint in gchipairs:
        if neutralinoPoint < mchi_lower or neutralinoPoint >= mchi_upper: continue
        if gluinoPoint < mg_lower or gluinoPoint >= mg_upper: continue
        if refXsecFile is not None:
            refXsec = 1.e3*gluinoHist.GetBinContent(gluinoHist.FindBin(gluinoPoint))
            print "INFO: ref xsec taken to be: %s mass %d, xsec = %f fb"%(gluinoHist.GetName(), gluinoPoint, refXsec)
        xsecRange = [refXsec]
        for xsecPoint in xsecRange:
            print "Now scanning mg = %.0f, mchi = %.0f, xsec = %.4f"%(gluinoPoint, neutralinoPoint, xsecPoint)
            for t in xrange(0,nJobs):
                xsecString = str(xsecPoint).replace(".","p")
                massPoint = "MG_%f_MCHI_%f"%(gluinoPoint, neutralinoPoint)
                output0 = model+"_"+massPoint+"_xsec"+xsecString+"_"+fitRegion+"_"+box+"_"+str(t)
                runJob = False
                if output0 not in outFileList: 
                    missingFiles+=1
                    runJob = True
                if not runJob: continue
                outputname,ffDir = writeBashScript(box,model,submitDir,neutralinoPoint,gluinoPoint,xsecPoint,fitRegion,signalRegion,t,nToys,significance,workspaceFlag,expected_a_priori)
                os.system("mkdir -p %s/%s"%(pwd,ffDir))
                totalJobs+=1
                os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                if not noSub:
                    time.sleep(3)
                    os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
    print "Missing files = ", missingFiles
    print "Total jobs = ", totalJobs
