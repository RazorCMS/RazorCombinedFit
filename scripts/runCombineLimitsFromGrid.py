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

    
def writeStep2BashScript(box,model,submitDir,neutralinoPoint,gluinoPoint,fitRegion):
    massPoint = "MG_%f_MCHI_%f"%(gluinoPoint, neutralinoPoint)
    t = 0
    # prepare the script to run
    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_"+fitRegion+"_"+box+"_"+str(t)+".src"
    outputfile = open(outputname,'w')

    label = {"MuEle":"MR300.0_R0.387298334621","EleEle":"MR300.0_R0.387298334621","MuMu":"MR300.0_R0.387298334621",
             "EleJet":"MR300.0_R0.387298334621","EleMultiJet":"MR300.0_R0.387298334621","MuMultiJet":"MR300.0_R0.387298334621","MuJet":"MR300.0_R0.387298334621",
             "MultiJet":"MR400.0_R0.5","Jet2b":"MR400.0_R0.5"}
    
    ffDir = outputDir+"/logs_"+model+"_"+massPoint+"_"+fitRegion+"_"+box
    user = os.environ['USER']
    
    combineDir = "/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/Combine/%s/"%(user[0],user,model)
    
    outputfile.write('#!/usr/bin/env bash -x\n')
    outputfile.write('mkdir -p %s\n'%combineDir)
    outputfile.write('echo $SHELL\n')
    outputfile.write('pwd\n')
    outputfile.write('cd /afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_1/src/RazorCombinedFit \n'%(user[0],user))
    outputfile.write('pwd\n')
    outputfile.write("export SCRAM_ARCH=slc5_amd64_gcc472\n")
    outputfile.write('eval `scramv1 runtime -sh`\n')
    outputfile.write('source setup.sh\n')
    outputfile.write('cd - \n')
    outputfile.write("export TWD=${PWD}/Razor2013_%s_%s_%s_%i\n"%(model,massPoint,box,t))
    outputfile.write("mkdir -p $TWD\n")
    outputfile.write("cd $TWD\n")
    outputfile.write('pwd\n')
    
    outputfile.write("export NAME=\"%s\"\n"%model)
    boxes =  box.split("_")
    seed = -1
    
    outputfile.write("cp %s/higgsCombineGrid${NAME}_%s_xsec*_%s_%s_%i.HybridNew.mH120.*.root $PWD\n"%(combineDir,massPoint,fitRegion,box,t))
    outputfile.write("cp %s/razor_combine_*_${NAME}_%s.* $PWD\n"%(combineDir,massPoint))
    outputfile.write("hadd -f higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root higgsCombineGrid${NAME}_%s_xsec*_%s_%s_%i.HybridNew.mH120.*.root\n"%(massPoint,fitRegion,box,t,massPoint,fitRegion,box,t))
    
    outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_1/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --grid=higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root --expectedFromGrid 0.025 -n Expected025${NAME}_%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,massPoint,fitRegion,box,t,massPoint,fitRegion,box,t,box,massPoint))
    outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_1/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --grid=higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root --expectedFromGrid 0.16 -n Expected160${NAME}_%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,massPoint,fitRegion,box,t,massPoint,fitRegion,box,t,box,massPoint))
    outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_1/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --grid=higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root --expectedFromGrid 0.50 -n Expected500${NAME}_%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,massPoint,fitRegion,box,t,massPoint,fitRegion,box,t,box,massPoint))
    outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_1/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --grid=higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root --expectedFromGrid 0.84 -n Expected840${NAME}_%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,massPoint,fitRegion,box,t,massPoint,fitRegion,box,t,box,massPoint))
    outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_1/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --grid=higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root --expectedFromGrid 0.975 -n Expected975${NAME}_%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,massPoint,fitRegion,box,t,massPoint,fitRegion,box,t,box,massPoint))
    outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_1/bin/slc5_amd64_gcc472/combine -M HybridNew --frequentist --grid=higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root -n Observed${NAME}_%s_%s_%s_%i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,massPoint,fitRegion,box,t,massPoint,fitRegion,box,t,box,massPoint))

    outputfile.write("hadd -f higgsCombineToys${NAME}_%s_%s_%s_%i.HybridNew.mH120.root higgsCombineExpected025*.root higgsCombineExpected160*.root higgsCombineExpected500*.root higgsCombineExpected840*.root higgsCombineExpected975*.root higgsCombineObserved*.root \n"%(massPoint,fitRegion,box,t))
    outputfile.write("cp $TWD/higgsCombineToys*.root %s \n"%combineDir)
    outputfile.write("cd; pwd; rm -rf $TWD\n")
    outputfile.close
    return outputname,ffDir
    
def writeStep1BashScript(box,model,submitDir,neutralinoPoint,gluinoPoint,xsecPoint,refXsec,fitRegion,signalRegion,t,nToys,iterations):
    massPoint = "MG_%f_MCHI_%f"%(gluinoPoint, neutralinoPoint)
    # prepare the script to run
    xsecString = str(xsecPoint).replace(".","p")
    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_xsec"+xsecString+"_"+fitRegion+"_"+box+"_"+str(t)+".src"
    outputfile = open(outputname,'w')
    
    label = {"MuEle":"MR300.0_R0.387298334621","EleEle":"MR300.0_R0.387298334621","MuMu":"MR300.0_R0.387298334621",
             "EleJet":"MR300.0_R0.387298334621","EleMultiJet":"MR300.0_R0.387298334621","MuMultiJet":"MR300.0_R0.387298334621","MuJet":"MR300.0_R0.387298334621",
             "MultiJet":"MR400.0_R0.5","Jet2b":"MR400.0_R0.5"}
        
    ffDir = outputDir+"/logs_"+model+"_"+massPoint+"_xsec"+xsecString+"_"+fitRegion+"_"+box
    user = os.environ['USER']
    
    combineDir = "/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/Combine/%s/"%(user[0],user,model)
    
    outputfile.write('#!/usr/bin/env bash -x\n')
    outputfile.write('mkdir -p %s\n'%combineDir)
    outputfile.write('echo $SHELL\n')
    outputfile.write('pwd\n')
    outputfile.write('cd /afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_1/src/RazorCombinedFit \n'%(user[0],user))
    outputfile.write('pwd\n')
    outputfile.write("export SCRAM_ARCH=slc5_amd64_gcc472\n")
    outputfile.write('eval `scramv1 runtime -sh`\n')
    outputfile.write('source setup.sh\n')
    outputfile.write('cd - \n')
    outputfile.write("export TWD=${PWD}/Razor2013_%s_%s_%s_%s_%i\n"%(model,massPoint,box,xsecString,t))
    outputfile.write("mkdir -p $TWD\n")
    outputfile.write("cd $TWD\n")
    outputfile.write('pwd\n')
    
    outputfile.write("export NAME=\"%s\"\n"%model)
    boxes =  box.split("_")
    seed = -1
    rSignal = float(xsecPoint/refXsec)
    
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/FULLFits2012ABCD_2Nov2013.root $PWD\n")
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/SidebandFits2012ABCD_2Nov2013.root $PWD\n")
    for ibox in boxes:
        outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/${NAME}/${NAME}_%s_%s_%s.root $PWD\n"%(massPoint,label[ibox],ibox))
        outputfile.write("python /afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_1/src/RazorCombinedFit/scripts/prepareCombine.py --box %s --model ${NAME} -i %sFits2012ABCD_2Nov2013.root ${NAME}_%s_%s_%s.root -c /afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_1/src/RazorCombinedFit/config_summer2012/RazorInclusive2012_3D_combine.config --xsec %f --signal-region %s\n"%(user[0],user,ibox,fitRegion,massPoint,label[ibox],ibox,user[0],user,refXsec,signalRegion))

    if len(boxes)>1:
        options = ["%s=razor_combine_%s_%s_%s.txt"%(ibox,ibox,model,massPoint) for ibox in boxes]
        option = " ".join(options)
        outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_1/bin/slc5_amd64_gcc472/combineCards.py %s > razor_combine_%s_%s_%s.txt \n"%(user[0],user,option,box,model,massPoint))
        if nToys>0: 
            outputfile.write("/afs/cern.ch/work/%s/%s/RAZORDMLIMITS/CMSSW_6_1_1/bin/slc5_amd64_gcc472/combine -M HybridNew -s %i --singlePoint %f --frequentist --saveHybridResult --saveToys --testStat LHC --fork 4 -T %i -n Grid${NAME}_%s_xsec%s_%s_%s_%i --clsAcc 0 --iterations %i razor_combine_%s_${NAME}_%s.txt\n"%(user[0],user,seed,rSignal,nToys,massPoint,xsecString,fitRegion,box,t,iterations,box,massPoint))
        
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
    model = sys.argv[2]
    queue = sys.argv[3]
    done  = sys.argv[4]
    mchi_lower = 0
    mchi_upper = 2025
    mg_lower = 0
    mg_upper = 2025
    refXsec = 100.
    refXsecFile = None
    fitRegion="Sideband"
    signalRegion="FULL"
    asymptoticFile="xsecUL_SMS_Razor.root"
    nToys = 3000
    iterations = 1
    step2 = False
    for i in xrange(5,len(sys.argv)):
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
        if sys.argv[i].find("--asymptotic-file")!=-1: asymptoticFile = sys.argv[i+1]
        if sys.argv[i].find("--fit-region")!=-1: fitRegion = sys.argv[i+1]
        if sys.argv[i].find("--signal-region")!=-1: signalRegion = sys.argv[i+1]
        if sys.argv[i].find("--toys")!=-1: nToys = int(sys.argv[i+1])

            
    if refXsecFile is not None:
        print "INFO: Input ref xsec file!"
        gluinoFile = rt.TFile.Open(refXsecFile,"READ")
        gluinoHistName = refXsecFile.split("/")[-1].split(".")[0]
        gluinoHist = gluinoFile.Get(gluinoHistName)
        
    nJobs = 1 # 
    nXsec = 5 # do 5 xsec points + 2 lower values + 1 higher value
    
    if asymptoticFile is not None:
        print "INFO: Input ref xsec file!"
        asymptoticRootFile = rt.TFile.Open(asymptoticFile,"READ")
        expMinus2 = asymptoticRootFile.Get("xsecUL_ExpMinus2_%s_%s"%(model,box))
        expPlus2 = asymptoticRootFile.Get("xsecUL_ExpPlus2_%s_%s"%(model,box))
        expMinus = asymptoticRootFile.Get("xsecUL_ExpMinus_%s_%s"%(model,box))
        expPlus = asymptoticRootFile.Get("xsecUL_ExpPlus_%s_%s"%(model,box))
        exp = asymptoticRootFile.Get("xsecUL_Exp_%s_%s"%(model,box))
        
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
                outItem = outFile.replace("higgsCombineGrid","").replace(".HybridNew.mH120","").replace(".root\n","")
                outItem = outItem.split(".")[:-1]
                outItem = ".".join(outItem)
                outFileList.append(outItem)
 
    totalJobs = 0
    missingFiles = 0
    for gluinoPoint, neutralinoPoint in gchipairs:

        if neutralinoPoint < mchi_lower or neutralinoPoint >= mchi_upper: continue
        if gluinoPoint < mg_lower or gluinoPoint >= mg_upper: continue

        massPoint = "MG_%f_MCHI_%f"%(gluinoPoint, neutralinoPoint)

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
            time.sleep(3)
            os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
            os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
        else:
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
            xsecRange = [minXsec + (maxXsec-minXsec)*float(i)/float(nXsec-1) for i in range(0,nXsec+1)]
            print xsecRange
            factorXsec = minXsec/(minXsec + (maxXsec-minXsec)/float(nXsec-1))
            print "factorXsec is", factorXsec
            xsecRange.reverse()
            xsecRange.append(minXsec*factorXsec)
            #xsecRange.append(minXsec*pow(factorXsec,2.0))
            xsecRange.append(minXsec*pow(factorXsec,4.0))
            xsecRange.reverse()
            print xsecRange
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
                    outputname,ffDir = writeStep1BashScript(box,model,submitDir,neutralinoPoint,gluinoPoint,xsecPoint,refXsec,fitRegion,signalRegion,t,nToys,iterations)
                    os.system("mkdir -p %s/%s"%(pwd,ffDir))
                    totalJobs+=1
                    time.sleep(3)
                    os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
    print "Missing files = ", missingFiles
    print "Total jobs = ", totalJobs
