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

def writeBashScript(box,sideband,fitmode,mg,mchi,xsec,nToys,nToysPerJob,t,doToys,doConvertToRoot,doFinalJob):
    pwd = os.environ['PWD']
    
    fitResultsDir = "FitResults_SignalInjection2"
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
    
    resultDir = "toys10k_%s_%s"%(datasetName,fitmode)
    toyDir = resultDir+"/%s_%s"%(xsecstring,box)
    ffDir = toyDir+"_FF"

    tagFR = ""
    tag3D = ""

    if box=="MuEle" or box=="MuMu" or box=="EleEle" or box=="TauTauJet":
        tagFR = "--fit-region=LowRsq_LowMR_HighMR"
    else:
        #tagFR = "--fit-region=LowRsq_LowMR_HighMR,LowRsq1b_LowMR1b_HighMR1b,LowRsq2b_LowMR2b_HighMR2b_LowRsq3b_LowMR3b_HighMR3b"
        tagFR = "--fit-region=LowRsq2b_LowMR2b_HighMR2b_LowRsq3b_LowMR3b_HighMR3b"

        
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
    #outputfile.write('eval `scramv1 runtime -sh` \n')
    outputfile.write("source setup.sh\n")
    outputfile.write("mkdir -p %s; mkdir -p %s; mkdir -p %s \n"%(resultDir,toyDir,ffDir))
    if doToys:
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c %s %s --fit-region %s -i %s --save-toys-from-fit %s -t %i --toy-offset %i --signal-injection -b \n"%(config,datasetMap[datasetName],sideband,fitResultMap[datasetName],toyDir,int(nToysPerJob),int(t*nToysPerJob)))
    if doConvertToRoot:
        outputfile.write("python scripts/convertToyToROOT.py %s/frtoydata_%s --start=%i --end=%i -b \n" %(toyDir, box, int(t*nToysPerJob),int(t*nToysPerJob)+nToysPerJob))
    if doFinalJob:
        #outputfile.write("rm %s.txt \n" %(toyDir))
        #outputfile.write("ls %s/frtoydata*.root > %s.txt \n" %(toyDir, toyDir))
        #outputfile.write("python scripts/expectedYield_sigbin.py 1 %s/expected_sigbin_%s.root %s %s.txt %s %s -b \n"%(ffDir, box, box, toyDir,tagFR,tag3D))
        outputfile.write("python scripts/makeToyPVALUE_sigbin.py %s %s/expected_sigbin_%s.root %s %s %s %s %s -b \n"%(box, ffDir, box, fitResultMap[datasetName], ffDir,tagFR,tag3D,tagPrintPlots))
        #outputfile.write("python scripts/make1DProj.py %s %s/expected_sigbin_%s.root %s %s -MC=%s %s %s %s -Label=%s_%s_%s -b \n"%(box,ffDir,box,fitResultMap[datasetName],ffDir,datasetName,tagFR,tag3D,tagPrintPlots,datasetName,xsecstring,box))
   
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
    box = sys.argv[2]
    sideband = 'Sideband'
    #fitmode = sys.argv[4]
    fitmode = '3D'
    queue = "8nh"
    nToys = 10000
    nJobs = 1
    
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
        xsecRange = [0.0, 0.001, 0.003, 0.005, 0.01, 0.04]
    else:
        xsecRange = [float(sys.argv[3])]

    mg = 1225
    mchi = 50
    
    nToysPerJob = int(nToys/nJobs)
    totalJobs = 0
    nJobsByBox = {}
    for box in boxNames:
        for xsec in xsecRange:
            xsecstring = str(xsec).replace(".","p")
            resultDir = "toys10k_%s_%s"%(datasetName,fitmode)
            toyDir = resultDir+"/%s_%s"%(xsecstring,box)
            ffDir = toyDir+"_FF"
            fullSetToys = ["%s/frtoydata_%s_%i.txt"%(toyDir,box,i) for i in xrange(0,nToys)]
            fullSetRoot = ["%s/frtoydata_%s_%i.root"%(toyDir,box,i) for i in xrange(0,nToys)]
            
            allToys = glob.glob("%s/*.txt"%(toyDir))
            allRoot = glob.glob("%s/*.root"%(toyDir))
            doFinalJob = (len(allToys)==nToys and len(allRoot)==nToys)
            
            nJobsByBox[(box,xsec)] = nJobs
            if doFinalJob:
                nJobsByBox[(box,xsec)] = 1
                missingToys = set([])
                missingRoot = set([])
            else:
                missingToys = set(fullSetToys) - set(allToys)
                missingRoot = set(fullSetRoot) - set(allRoot)

            if glob.glob("%s/expected_sigbin_%s.root"%(ffDir,box)): doFinalJob = False

            doFinalJob = True
            for t in xrange(0,nJobsByBox[(box,xsec)]):
                doToys = False
                doConvertToRoot = False
                for i in xrange(int(t*nToysPerJob),int((t+1)*nToysPerJob)):
                    if "%s/frtoydata_%s_%i.txt"%(toyDir,box,i) in missingToys: doToys = True
                    if "%s/frtoydata_%s_%i.root"%(toyDir,box,i) in missingRoot: doConvertToRoot = True

                doFinalJob = True
                doToys = False
                doConvertToRoot = False
                if doFinalJob or doToys or doConvertToRoot:
                    outputname,ffDir,pwd = writeBashScript(box,sideband,fitmode,mg,mchi,xsec,nToys,nToysPerJob,t,doToys,doConvertToRoot,doFinalJob)
                    totalJobs+=1
                    #time.sleep(3)
                    #os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    #os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    #os.system("source "+pwd+"/"+outputname)
                
    print "TOTAL JOBS IS %i"%totalJobs
