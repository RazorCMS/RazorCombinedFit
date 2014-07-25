#! /usr/bin/env python
from optparse import OptionParser
import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys, re
import time
from math import *
from array import *
from getGChiPairs import *

    
def writeStep2BashScript(box,model,submitDir,neutralinoPoint,gluinoPoint,fitRegion):
    massPoint = "%0.1f_%0.1f"%(gluinoPoint, neutralinoPoint)
   
    t = 0
    # prepare the script to run
    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_"+fitRegion+"_"+box+"_"+str(t)+".src"
    outputfile = open(outputname,'w')

    label = {"Mu":"MR350.0_R0.282842712475",
             "Ele":"MR350.0_R0.282842712475"}
    
    ffDir = outputDir+"/logs_"+model+"_"+massPoint+"_"+fitRegion+"_"+box
    user = os.environ['USER']
    
    combineDir = "/afs/cern.ch/work/%s/%s/private/RAZORLIMITS/Combine/%s/"%(user[0],user,model)
    
    outputfile.write('#!/usr/bin/env bash -x\n')
    outputfile.write('mkdir -p %s\n'%combineDir)
    outputfile.write('echo $SHELL\n')
    outputfile.write('pwd\n')
    outputfile.write('cd /afs/cern.ch/user/l/lucieg/scratch1/Mar28_combine/CMSSW_6_1_2/src/RazorCombinedFit/ \n')
    outputfile.write('pwd\n')
    outputfile.write("export SCRAM_ARCH=slc5_amd64_gcc472\n")
    outputfile.write('eval `scramv1 runtime -sh`\n')
    outputfile.write('source setup.sh\n')
    outputfile.write('cd - \n')
    outputfile.write("export TWD=/afs/cern.ch/work/l/lucieg/private//Razor2013%s_%s_%s_%i\n"%(model,massPoint,box,t))
    outputfile.write("mkdir -p $TWD\n")
    outputfile.write("cd $TWD\n")
    outputfile.write('pwd\n')
    
    outputfile.write("export NAME=\"%s\"\n"%model)
    boxes =  box.split("_")
    seed = -1
    
    outputfile.write("cp %s/higgsCombineGrid${NAME}_%s_xsec*_%s_%s_*.HybridNew.mH120.*.root $PWD\n"%(combineDir,massPoint,fitRegion,box))
    outputfile.write("cp %s/razor_combine_*_${NAME}_%s.* $PWD\n"%(combineDir,massPoint))
    outputfile.write("hadd -f higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root higgsCombineGrid${NAME}_%s_xsec*_%s_%s_*.HybridNew.mH120.*.root\n"%(massPoint,fitRegion,box,t,massPoint,fitRegion,box))
    
    outputfile.write("/afs/cern.ch/user/l/lucieg/scratch1/Mar28_combine/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --grid=higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root --expectedFromGrid 0.025 -n Expected025${NAME}_%s_%s_%s_%i razor_combine_%s_%s_${NAME}_%s.txt --rMax 100000.\n"%(massPoint,fitRegion,box,t,massPoint,fitRegion,box,t,box,njets,massPoint))
    outputfile.write("/afs/cern.ch/user/l/lucieg/scratch1/Mar28_combine/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --grid=higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root --expectedFromGrid 0.16 -n Expected160${NAME}_%s_%s_%s_%i razor_combine_%s_%s_${NAME}_%s.txt --rMax 100000.\n"%(massPoint,fitRegion,box,t,massPoint,fitRegion,box,t,box,njets,massPoint))
    outputfile.write("/afs/cern.ch/user/l/lucieg/scratch1/Mar28_combine/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --grid=higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root --expectedFromGrid 0.50 -n Expected500${NAME}_%s_%s_%s_%i razor_combine_%s_%s_${NAME}_%s.txt --rMax 100000.\n"%(massPoint,fitRegion,box,t,massPoint,fitRegion,box,t,box,njets,massPoint))
    outputfile.write("/afs/cern.ch/user/l/lucieg/scratch1/Mar28_combine/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --grid=higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root --expectedFromGrid 0.84 -n Expected840${NAME}_%s_%s_%s_%i razor_combine_%s_%s_${NAME}_%s.txt --rMax 100000.\n"%(massPoint,fitRegion,box,t,massPoint,fitRegion,box,t,box,njets,massPoint))
    outputfile.write("/afs/cern.ch/user/l/lucieg/scratch1/Mar28_combine/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --grid=higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root --expectedFromGrid 0.975 -n Expected975${NAME}_%s_%s_%s_%i razor_combine_%s_%s_${NAME}_%s.txt --rMax 100000.\n"%(massPoint,fitRegion,box,t,massPoint,fitRegion,box,t,box,njets,massPoint))
    outputfile.write("/afs/cern.ch/user/l/lucieg/scratch1/Mar28_combine/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --grid=higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root -n Observed${NAME}_%s_%s_%s_%i razor_combine_%s_%s_${NAME}_%s.txt --rMax 100000.\n"%(massPoint,fitRegion,box,t,massPoint,fitRegion,box,t,box,njets,massPoint))

    outputfile.write("hadd -f higgsCombineToys${NAME}_%s_%s_%s_%i.HybridNew.mH120.root higgsCombineExpected025*.root higgsCombineExpected160*.root higgsCombineExpected500*.root higgsCombineExpected840*.root higgsCombineExpected975*.root higgsCombineObserved*.root \n"%(massPoint,fitRegion,box,t))
    outputfile.write("cp $TWD/higgsCombineToys*.root %s \n"%combineDir)
    outputfile.write("cd; pwd; rm -rf $TWD\n")
    outputfile.close
    return outputname,ffDir
    
def writeStep1BashScript(box,model,submitDir,neutralinoPoint,gluinoPoint,xsecPoint,refXsec,fitRegion,signalRegion,t,nToysPerJob,iterations,workspaceFlag,penalty,njets):
    massPoint = "%0.1f_%0.1f"%(gluinoPoint, neutralinoPoint)
    workspaceString = ""
    if workspaceFlag:
        workspaceString = "Workspace"
    penaltyString = ""
    if penalty:
        penaltyString = "--penalty"
    # prepare the script to run
    xsecString = str(xsecPoint).replace(".","p")
    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_xsec"+xsecString+"_"+fitRegion+"_"+box+"_"+str(t)+".src"
    outputfile = open(outputname,'w')
    
    label = {"Mu":"MR350.0_R0.282842712475",
             "Ele":"MR350.0_R0.282842712475"}

    ffDir = outputDir+"/logs_"+model+"_"+massPoint+"_xsec"+xsecString+"_"+fitRegion+"_"+box
    user = os.environ['USER']
    
    combineDir = "/afs/cern.ch/work/%s/%s/private/RAZORLIMITS/Combine/%s/"%(user[0],user,model)
   
    outputfile.write('#!/usr/bin/env bash -x\n')
    outputfile.write('mkdir -p %s\n'%combineDir)
    outputfile.write('echo $SHELL\n')
    outputfile.write('pwd\n')
    outputfile.write('cd /afs/cern.ch/user/l/lucieg/scratch1/Mar28_combine/CMSSW_6_1_2/src/RazorCombinedFit/ \n')
    outputfile.write('pwd\n')
    outputfile.write("export SCRAM_ARCH=slc5_amd64_gcc472\n")
    outputfile.write('eval `scramv1 runtime -sh`\n')
    outputfile.write('source setup.sh\n')
    outputfile.write('cd - \n')
    outputfile.write("export TWD=/afs/cern.ch/work/l/lucieg/private/Razor2013%s_%s_%s_%s_%i\n"%(model,massPoint,box,xsecString,t))
    outputfile.write("mkdir -p $TWD\n")
    outputfile.write("cd $TWD\n")
    outputfile.write('pwd\n')
    
    outputfile.write("export NAME=\"%s\"\n"%model)
    boxes =  box.split("_")
    sparticle = "stop"
    if model.find("T1")!=-1:
        sparticle = "gluino"
    seed = -1
    rSignal = float(xsecPoint)/refXsec

    outputfile.write("cp /afs/cern.ch/user/l/lucieg/scratch1/Oct18/CMSSW_6_2_0/src/RazorCombinedFit/FitResults/razor_Single%s3D_%s_%s_%s.root $PWD\n"%(box,njets,box,fitRegion))
    mLSP = int(float(re.split('_',massPoint)[-1]))
    SMS = 'SMS-T2tt_mStop-Combo_mLSP_%s.0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY_MR350.0_R0.282842712475'%mLSP
    outputfile.write("cp /afs/cern.ch/work/l/lucieg/private/MC_test/%s%s%s/mLSP%s/%s_%s_%s.root $PWD/%s_%s_%s_%s.root \n"%(model, box, njets, mLSP, SMS, massPoint, box, SMS, njets, massPoint, box))

    outputfile.write("python /afs/cern.ch/user/l/lucieg/scratch1/Mar28_combine/CMSSW_6_1_2/src/RazorCombinedFit/scripts/prepareCombineWorkspace.py --box %s_%s --model %s -i razor_Single%s3D_%s_%s_%s.root -c /afs/cern.ch/user/l/lucieg/scratch1/Oct18/CMSSW_6_2_0/src/RazorCombinedFit/config_summer2012/RazorMultiJet2013_3D_hybrid.config --xsec %f  %s_%s_%s_%s.root \n"%(box, njets, model, box, njets, box, fitRegion, xsecPoint, SMS, njets, massPoint, box))
   
    outputfile.write("/afs/cern.ch/user/l/lucieg/scratch1/Mar28_combine/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine -M HybridNew -s %i --singlePoint %f --frequentist --saveHybridResult --saveToys --testStat LHC --fork 4 -T %i --fullBToys -n Grid${NAME}_%s_xsec%s_%s_%s_%i --clsAcc 0 --iterations %i\
    razor_combine_%s_%s_${NAME}_%s.txt --rMax 100000.\n"%(seed,rSignal,nToysPerJob,massPoint,xsecString,fitRegion,box, t,iterations,box,njets,massPoint))
        
    outputfile.write("cp $TWD/higgsCombine*.root %s \n"%combineDir)
    outputfile.write("cp $TWD/razor_combine_*.* %s \n"%combineDir)
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
    name = re.split('_', box)
    box   = name[0]
    njets = name[1]
   
    model = sys.argv[2]
    queue = sys.argv[3]
    done  = sys.argv[4]
    mchi_lower = 0
    mchi_upper = 2025
    mg_lower = 0
    mg_upper = 2025

    refXsecs = {150:80.268,
                175:36.7994,
                200:18.5245,
                225:9.90959,
                250:5.57596,
                275:3.2781,
                300:1.99608,
                325:1.25277,
                350:0.807323,
                375:0.531443,
                400:0.35683,
                425:0.243755,
                450:0.169688,
                475:0.119275,
                500:0.0855847,
                525:0.0618641,
                550:0.0452067,
                575:0.0333988,
                600:0.0248009,
                625:0.0185257,
                650:0.0139566,
                675:0.0106123,
                700:0.0081141,
                725:0.00623244,
                750:0.00480639,
                775:0.00372717}
    
    refXsecFile = None
    fitRegion="FULL"#Sideband
    signalRegion="FULL"
    asymptoticFile=None#"asymptoticFileMugt4jets.root"
    nToys = 3000 # do 3000 total toys
    nJobs = 1 # split the toys over 1 jobs 
    iterations = 1
    step2 = True
    workspaceFlag = True
    noSub = False
    penalty = False
    for i in xrange(5,len(sys.argv)):
        if sys.argv[i].find("--no-sub")!=-1: noSub = True
        if sys.argv[i].find("--step2")!=-1: step2 = True        
        if sys.argv[i].find("--mchi-lt")!=-1: mchi_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mchi-geq")!=-1: mchi_lower = float(sys.argv[i+1])
        if sys.argv[i].find("--mg-lt")!=-1: mg_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mg-geq")!=-1: mg_lower = float(sys.argv[i+1])
        if sys.argv[i].find("--iterations")!=-1: iterations = int(sys.argv[i+1])
        if sys.argv[i].find("--xsec")!=-1: 
            if sys.argv[i].find("--xsec-file")!=-1: 
                refXsecFile = sys.argv[i+1]
            else:
                refXsec = float(sys.argv[i+1])
        #if sys.argv[i].find("--asymptotic-file")!=-1: asymptoticFile = sys.argv[i+1]
        if sys.argv[i].find("--fit-region")!=-1: fitRegion = sys.argv[i+1]
        if sys.argv[i].find("--signal-region")!=-1: signalRegion = sys.argv[i+1]
        if sys.argv[i].find("--toys")!=-1: nToys = int(sys.argv[i+1])
        if sys.argv[i].find("--jobs")!=-1: nJobs = int(sys.argv[i+1])
        if sys.argv[i].find("--work")!=-1: workspaceFlag = True
        if sys.argv[i].find("--no-work")!=-1: workspaceFlag = False
        if sys.argv[i].find("--penalty")!=-1: penalty = True

    ###I'm not using this        
    if refXsecFile is not None:
        print "INFO: Input ref xsec file!", refXsecFile
        gluinoFile = rt.TFile.Open(refXsecFile,"READ")
        gluinoHistName = refXsecFile.split("/")[-1].split(".")[0]
        gluinoHist = gluinoFile.Get(gluinoHistName)
        
    nToysPerJob = int(nToys/nJobs)
    nXsec = 5 # do 5 xsec points + 0 lower values + 1 higher value
    #instead I had tried :
    xsecRanges = {


        150: [],
        175: [],
        200: [],
        225: [72.],
        250: [60.],
        275: [],
        300: [],
        325: [],
        350: [],
        375: [],
        400: [],
        425: [],
        450: [],
        475: [],
        500: [],
        525: [23.],
        550:[],
        575:[],
        600:[],
        625:[],
        650:[],
        675:[],
        700:[],
        725:[],
        750:[],
        775:[],
        }
    ###

    ###Getting asymptotic limits as input
    if asymptoticFile is not None:
        print "INFO: Input ref xsec file!"
        asymptoticRootFile = rt.TFile.Open(asymptoticFile,"READ")
        expMinus2 = asymptoticRootFile.Get("xsecUL_ExpMinus2_%s_%s"%(model,box))
        expPlus2 = asymptoticRootFile.Get("xsecUL_ExpPlus2_%s_%s"%(model,box))
        expMinus = asymptoticRootFile.Get("xsecUL_ExpMinus_%s_%s"%(model,box))
        expPlus = asymptoticRootFile.Get("xsecUL_ExpPlus_%s_%s"%(model,box))
        exp = asymptoticRootFile.Get("xsecUL_Exp_%s_%s"%(model,box))
    ###
        
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
    outFileList = []
    if step2:
        for outFile in doneFile.readlines():
            if outFile.find("higgsCombineObserved%s"%model)!=-1:
                outItem = outFile.replace("higgsCombineObserved","").replace(".HybridNew.mH120","").replace(".root\n","")
                outFileList.append(outItem)
    else:
        for outFile in doneFile.readlines():
            if outFile.find("higgsCombineGrid%s"%model)!=-1:
                outItem = outFile.replace("/afs/cern.ch/work/l/lucieg/private/RAZORLIMITS/Combine/T2tt/","").replace("higgsCombineGrid","").replace(".HybridNew.mH120","").replace(".root\n","")
                outItem = outItem.split(".")[:-1]
                outItem = ".".join(outItem)
                outFileList.append(outItem)
        
    totalJobs = 0
    missingFiles = 0
  
    for gluinoPoint, neutralinoPoint in gchipairs:

        if neutralinoPoint < mchi_lower or neutralinoPoint >= mchi_upper: continue
        if gluinoPoint < mg_lower or gluinoPoint >= mg_upper: continue
        #if not(gluinoPoint ==550 ):continue
        if not(neutralinoPoint == 25):continue
        
        massPoint = "%.1f_%.1f"%(gluinoPoint, neutralinoPoint)

        if step2:
            t = 0
            print "Now scanning mg = %.0f, mchi = %.0f"%(gluinoPoint, neutralinoPoint)
            output0 = model+"_"+massPoint+"_"+fitRegion+"_"+box+"_"+str(t)
            runJob = False
            if output0 not in outFileList: 
                    missingFiles+=1
                    runJob = True
            if not runJob: continue
            outputname,ffDir = writeStep2BashScript(box,model,submitDir,neutralinoPoint,gluinoPoint,fitRegion)
            os.system("mkdir -p %s/%s"%(pwd,ffDir))
            totalJobs+=1
            os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
            if not noSub:
                time.sleep(3)
                os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
        else:
            if asymptoticFile is not None :
                minXsec = 1.e3*expPlus2.GetBinContent(expPlus2.FindBin(gluinoPoint,neutralinoPoint))
                maxXsec = 1.e3*expMinus2.GetBinContent(expMinus2.FindBin(gluinoPoint,neutralinoPoint))
                print "expPlus2  = %f "%(1.e3*expPlus2.GetBinContent(expPlus2.FindBin(gluinoPoint,neutralinoPoint)))
                print "expPlus   = %f "%(1.e3*expPlus.GetBinContent(expPlus.FindBin(gluinoPoint,neutralinoPoint)))
                print "exp       = %f "%(1.e3*exp.GetBinContent(exp.FindBin(gluinoPoint,neutralinoPoint)))
                print "expMinus  = %f "%(1.e3*expMinus.GetBinContent(expMinus.FindBin(gluinoPoint,neutralinoPoint)))
                print "expMinus2 = %f "%(1.e3*expMinus2.GetBinContent(expMinus2.FindBin(gluinoPoint,neutralinoPoint)))
                if maxXsec==0 and minXsec==0: continue
                if refXsecFile is not None:
                    refXsec = 1.e3*gluinoHist.GetBinContent(gluinoHist.FindBin(gluinoPoint))
                    print "INFO: ref xsec taken to be: %s mass %d, ref xsec = %f fb"%(gluinoHist.GetName(), gluinoPoint, refXsec)
                else :
                    refXsec = 1.#refXsecs[gluinoPoint]

               ##  xsecRange = [minXsec + (maxXsec-minXsec)*float(i)/float(nXsec-1) for i in range(0,nXsec+1)]
##                 print '1   ',xsecRange 
##                 xsecRange = [(maxXsec - (maxXsec-minXsec)*float(i)/float(nXsec-1))*0.1 for i in range(0,nXsec+1)]
##                 print '2   ',xsecRange 
                xsecRange = [(maxXsec - (maxXsec-minXsec)*float(i)/float(nXsec-1))*0.05 for i in range(0,nXsec+1)]
                print '3   ',xsecRange 
               
            else :
                refXsec = 1.
                xsecRange = xsecRanges[gluinoPoint]
            #factorXsec = minXsec/(minXsec + (maxXsec-minXsec)/float(nXsec-1))
            #print "factorXsec is", factorXsec
            #xsecRange.reverse()
            #xsecRange.append(minXsec*factorXsec)
            #xsecRange.append(minXsec*pow(factorXsec,2.0))
            #xsecRange.append(minXsec*pow(factorXsec,4.0))
            #xsecRange.reverse()
            for xsecPoint in xsecRange:
                if xsecPoint<=0: continue
                xsecString = str(xsecPoint).replace(".","p")
                print "Now scanning mg = %.0f, mchi = %.0f, xsec = %.4f"%(gluinoPoint, neutralinoPoint, xsecPoint)
                for t in xrange(0,nJobs):
                    output0 = model+"_"+massPoint+"_xsec"+xsecString+"_"+fitRegion+"_"+box+"_"+str(t)
                    runJob = False
                    if output0 not in outFileList: 
                        missingFiles+=1
                        runJob = True
                    if not runJob: continue
                    outputname,ffDir = writeStep1BashScript(box,model,submitDir,neutralinoPoint,gluinoPoint,xsecPoint,refXsec,fitRegion,signalRegion,t,nToysPerJob,iterations,workspaceFlag,penalty,njets)
                    os.system("mkdir -p %s/%s"%(pwd,ffDir))
                    totalJobs+=1
                    os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    if not noSub:
                        time.sleep(3)
                        os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
    print "Missing files = ", missingFiles
    print "Total jobs = ", totalJobs
