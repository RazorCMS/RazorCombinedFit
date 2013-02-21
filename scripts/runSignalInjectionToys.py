#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys
from array import *
import time

def writeBashScript(box,sideband,fitmode,mg,mchi,xsec,nToys,nToysPerJob,t):
    pwd = os.environ['PWD']
    
    fitResultsDir = "FitResults_SignalInjection"
    config = "config_summer2012/RazorInclusive2012_%s_hybrid.config"%fitmode

    submitDir = "submit"
    
    xsecstring = str(xsec).replace(".","p")
    fitResultMap = {'T1bbbb':'%s/razor_output_T1bbbb_MG_%f_MCHI_%f_xsec_%s_%s.root'%(fitResultsDir,mg,mchi,xsecstring,box)}
    
    if box == "TauTauJet" or box=="Jet" or box=="MultiJet":
        mRmin = 400.
        rMin = 0.5
    else:
        mRmin = 300.
        rMin = 0.387298334621
        
    label = "MR"+str(mRmin)+"_R"+str(rMin)
    datasetMap = {'T1bbbb':'SMS/T1bbbb_MG_%f_MCHI_%f_%s_%s.root'%(mg,mchi,label,box)}
    
    resultDir = "toys_%s_%s"%(datasetName,fitmode)
    toyDir = resultDir+"/%s_%s"%(xsecstring,box)
    ffDir = toyDir+"_FF"

    tagFR = ""
    tag3D = ""

    if box=="MuEle" or box=="MuMu" or box=="EleEle" or box=="TauTauJet":
        tagFR = "--fit-region=LowRsq_LowMR_HighMR"
    else:
        tagFR = "--fit-region=LowRsq_LowMR_HighMR,LowRsq1b_LowMR1b_HighMR1b,LowRsq2b_LowMR2b_HighMR2b_LowRsq3b_LowMR3b_HighMR3b"

        
    if fitmode == "3D":
        tag3D = "--3D"
        
    tagPrintPlots = "--printPlots"
        
    os.system("mkdir -p %s"%(submitDir)) 
    # prepare the script to run
    outputname = submitDir+"/submit_"+datasetName+"_"+fitmode+"_"+xsecstring+"_"+box+"_"+str(t)+".src"
    outputfile = open(outputname,'w')
    outputfile.write('#!/bin/bash\n')
    outputfile.write('cd %s \n'%pwd)
    outputfile.write('echo $PWD \n')
    outputfile.write('eval `scramv1 runtime -sh` \n')
    outputfile.write("source /afs/cern.ch/sw/lcg/external/gcc/4.3.2/x86_64-slc5/setup.sh\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.34.05/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh\n")
    outputfile.write("mkdir -p %s; mkdir -p %s; mkdir -p %s \n"%(resultDir,toyDir,ffDir))
    if nToys <= nToysPerJob:
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c %s %s --fit-region %s -i %s --save-toys-from-fit %s -t %i --toy-offset %i --signal-injection -b \n"%(config,datasetMap[datasetName],sideband,fitResultMap[datasetName],toyDir,int(nToys),0))
    else:
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c %s %s --fit-region %s -i %s --save-toys-from-fit %s -t %i --toy-offset %i --signal-injection -b \n"%(config,datasetMap[datasetName],sideband,fitResultMap[datasetName],toyDir,int(nToysPerJob),int(t*nToysPerJob)))
    outputfile.write("python scripts/convertToyToROOT.py %s/frtoydata_%s --start=%i --end=%i -b \n" %(toyDir, box, int(t*nToysPerJob),int(t*nToysPerJob)+nToysPerJob))
    outputfile.write("files=$(ls %s/frtoydata_*.root 2> /dev/null | wc -l) \n"%toyDir)
    outputfile.write("if [ $files == \"%i\" ] \n"%nToys)
    outputfile.write("then \n")
    outputfile.write("rm %s.txt \n" %(toyDir))
    outputfile.write("ls %s/frtoydata_*.root > %s.txt \n" %(toyDir, toyDir))
    outputfile.write("python scripts/expectedYield_sigbin.py 1 %s/expected_sigbin_%s.root %s %s.txt %s %s -b \n"%(ffDir, box, box, toyDir,tagFR,tag3D))
    outputfile.write("python scripts/makeToyPVALUE_sigbin.py %s %s/expected_sigbin_%s.root %s %s %s %s %s -b \n"%(box, ffDir, box, fitResultMap[datasetName], ffDir,tagFR,tag3D,tagPrintPlots))
    outputfile.write("python scripts/make1DProj.py %s %s/expected_sigbin_%s.root %s %s -MC=%s %s %s %s -b \n"%(box,ffDir,box,fitResultMap[datasetName],ffDir,datasetName,tagFR,tag3D,tagPrintPlots))
   
    outputfile.write("fi \n") 
    outputfile.close

    return outputname, ffDir, pwd

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "\nRun the script as follows:\n"
        print "python scripts/runToys DatasetName BoxName FitRegion"
        print "with:"
        print "   DatasetName = name of the sample (TTJets, WJets, SMCocktail, MuHad-Run2012ABCD, ElectronHad-Run2012ABCD, etc)"
        print "   BoxName = name of the Box (MuMu, MuEle, etc, or All)"
        print "   FitRegion = name of the fit region (FULL, Sideband, or All)"
        print ""
        print "After the inputs you can specify the following options"
        print "--q=queue"
        print "--t=number of toys"
        sys.exit()
    
    datasetName = sys.argv[1]
    fitmode = '3D'
    queue = "1nd"
    nToys = 3000
    nJobs = 12
    
    for i in range(4,len(sys.argv)):
        if sys.argv[i].find("--q=") != -1:
            queue = sys.argv[i].replace("--q=","")
        if sys.argv[i].find("--t=") != -1:
            nToys = int(sys.argv[i].replace("--t=",""))
        if sys.argv[i].find("--j=") != -1:
            nJobs = int(sys.argv[i].replace("--j=",""))

    if sys.argv[2]=='All':
        boxNames = ['MuEle','MuMu','EleEle','EleTau','Ele','MuTau','Mu','TauTauJet','Jet','MultiJet']
    else:
        boxNames = [sys.argv[2]]

    
    if sys.argv[3]=='All':
        xsecRange = [0.0005, 0.001, 0.005, 0.01, 0.05]
    else:
        xsecRange = [float(sys.argv[3])]

    mg = 1225
    mchi = 0

    
    sideband = 'Sideband'
    
    nToysPerJob = int(nToys/nJobs)
    for box in boxNames:
        for xsec in xsecRange:
            if nToys <= nToysPerJob:
                outputname,ffDir,pwd = writeBashScript(box,sideband,fitmode,mg,mchi,xsec,nToys,nToysPerJob,0)
                time.sleep(3)
                os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(0)+".log source "+pwd+"/"+outputname)
                os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(0)+".log source "+pwd+"/"+outputname)
                #os.system("source "+pwd+"/"+outputname)
            else:
                for t in xrange(0,nJobs):
                    outputname,ffDir,pwd = writeBashScript(box,sideband,fitmode,mg,mchi,xsec,nToys,nToysPerJob,t)
                    time.sleep(3)
                    os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    #os.system("source "+pwd+"/"+outputname)
