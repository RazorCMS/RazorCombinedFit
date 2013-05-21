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

def writeBashScript(box,sideband,fitmode,nToys,nToysPerJob,t,doToys,doConvertToRoot,doFinalJob):
    pwd = os.environ['PWD']
            
    #fitResultsDir = "FitResults_%s"%fitmode
    fitResultsDir = "FitResults_NOTAU"
    config = "config_summer2012/RazorInclusive2012_%s_hybrid.config"%fitmode

    submitDir = "submit"
    
    # fitResultMap = {'WJets':'%s/razor_output_WJets_%s_%s.root'%(fitResultsDir,sideband,box),
    #                 'TTJets':'%s/razor_output_TTJets_%s_%s.root'%(fitResultsDir,sideband,box),
    #                 'ZJetsToNuNu':'%s/razor_output_ZJetsToNuNu_%s_%s.root'%(fitResultsDir,sideband,box),
    #                 'SMCocktail':'%s/razor_output_SMCocktail_%s_%s.root'%(fitResultsDir,sideband,box),
    #                 'MuHad-Run2012ABCD':'%s/razor_output_MuHad-Run2012ABCD_%s_%s.root'%(fitResultsDir,sideband,box),
    #                 'ElectronHad-Run2012ABCD':'%s/razor_output_ElectronHad-Run2012ABCD_%s_%s.root'%(fitResultsDir,sideband,box),
    #                 'HT-HTMHT-Run2012ABCD':'%s/razor_output_HT-HTMHT-Run2012ABCD_%s_%s.root'%(fitResultsDir,sideband,box)}
    fitResultMap = {'MuHad-Run2012ABCD':'%s/%sFits2012ABCD_FrenchFlags.root'%(fitResultsDir,sideband),
                    'ElectronHad-Run2012ABCD':'%s/%sFits2012ABCD_FrenchFlags.root'%(fitResultsDir,sideband),
                    'HT-HTMHT-Run2012ABCD':'%s/%sFits2012ABCD_FrenchFlags.root'%(fitResultsDir,sideband)}
    if box == "TauTauJet" or box=="Jet1b" or box=="Jet2b" or box=="MultiJet":
        mRmin = 400.
        rMin = 0.5
    else:
        mRmin = 300.
        rMin = 0.387298334621
        
    label = "MR"+str(mRmin)+"_R"+str(rMin)
    datasetMap = {'WJets':'MC/WJetsToLNu_%s_BTAG_PF_%s.root'%(label,box),
                  'TTJets':'MC/TTJets_%s_BTAG_PF_%s.root'%(label,box),
                  'ZJetsToNuNu':'MC/ZJetsToNuNu_GENTOY_%s_%s.root'%(label,box),
                  'SMCocktail':'MC/SMCocktail_GENTOY_%s_%s.root'%(label,box),
                  'MuHad-Run2012ABCD':'DATA_NOTAU/MuHad-Run2012ABCD_%s_BTAG_PF_%s.root'%(label,box),
                  'ElectronHad-Run2012ABCD':'DATA_NOTAU/ElectronHad-Run2012ABCD_%s_BTAG_PF_%s.root'%(label,box),
                  'HT-HTMHT-Run2012ABCD':'DATA_NOTAU/HT-HTMHT-Run2012ABCD_%s_BTAG_PF_%s.root'%(label,box)}
    resultDir = "toys10k_%s_%s"%(datasetName,fitmode)
    toyDir = resultDir+"/%s_%s"%(sideband,box)
    ffDir = toyDir+"_FF"

    tagFR = ""
    tag3D = ""

    if box=="MuEle" or box=="MuMu" or box=="EleEle" or box=="TauTauJet" or box=="Jet1b" or box=="Jet2b":
        tagFR = "--fit-region=LowRsq_LowMR_HighMR"
    else:
        tagFR = "--fit-region=LowRsq_LowMR_HighMR,LowRsq1b_LowMR1b_HighMR1b,LowRsq2b_LowMR2b_HighMR2b_LowRsq3b_LowMR3b_HighMR3b"

        
    if fitmode == "3D":
        tag3D = "--3D"
        
    tagPrintPlots = "--printPlots"
        
    os.system("mkdir -p %s"%(submitDir)) 
    # prepare the script to run
    outputname = submitDir+"/submit_"+datasetName+"_"+fitmode+"_"+sideband+"_"+box+"_"+str(t)+".src"
    outputfile = open(outputname,'w')
    outputfile.write('#!/bin/bash\n')
    outputfile.write('cd %s \n'%pwd)
    outputfile.write('echo $PWD \n')
    outputfile.write('eval `scramv1 runtime -sh` \n')
    outputfile.write("source setup.sh\n")
    outputfile.write("mkdir -p %s; mkdir -p %s; mkdir -p %s \n"%(resultDir,toyDir,ffDir))
    if doToys:
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c %s %s --fit-region %s -i %s --save-toys-from-fit %s -t %i --toy-offset %i -b \n"%(config,datasetMap[datasetName],sideband,fitResultMap[datasetName],toyDir,int(nToysPerJob),int(t*nToysPerJob)))
    if doConvertToRoot:
        outputfile.write("python scripts/convertToyToROOT.py %s/frtoydata_%s --start=%i --end=%i -b \n" %(toyDir, box, int(t*nToysPerJob),int(t*nToysPerJob)+nToysPerJob))
    if doFinalJob:
        outputfile.write("rm %s.txt \n" %(toyDir))
        outputfile.write("ls %s/frtoydata*.root > %s.txt \n" %(toyDir, toyDir))
        outputfile.write("python scripts/expectedYield_sigbin.py 1 %s/expected_sigbin_%s.root %s %s.txt %s %s -b \n"%(ffDir, box, box, toyDir,tagFR,tag3D))
        outputfile.write("python scripts/makeToyPVALUE_sigbin.py %s %s/expected_sigbin_%s.root %s %s %s %s %s -b \n"%(box, ffDir, box, fitResultMap[datasetName], ffDir,tagFR,tag3D,tagPrintPlots))
        if datasetName.find("Run") != -1:
            outputfile.write("python scripts/make1DProj.py %s %s/expected_sigbin_%s.root %s %s %s %s %s -Label=%s_%s_%s -b \n"%(box,ffDir,box,fitResultMap[datasetName],ffDir,tagFR,tag3D,tagPrintPlots,datasetName,sideband,box))
        else:
            outputfile.write("python scripts/make1DProj.py %s %s/expected_sigbin_%s.root %s %s -MC=%s %s %s %s -Label=%s_%s_%s -b \n"%(box,ffDir,box,fitResultMap[datasetName],ffDir,datasetName,tagFR,tag3D,tagPrintPlots,datasetName,sideband,box))
   
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
    sideband = sys.argv[3]
    #fitmode = sys.argv[4]
    fitmode = '3D'
    queue = "8nh"
    nToys = 10000
    nJobs = 50
    
    for i in range(4,len(sys.argv)):
        if sys.argv[i].find("--q=") != -1:
            queue = sys.argv[i].replace("--q=","")
        if sys.argv[i].find("--t=") != -1:
            nToys = int(sys.argv[i].replace("--t=",""))
        if sys.argv[i].find("--j=") != -1:
            nJobs = int(sys.argv[i].replace("--j=",""))

    if sys.argv[2]=='All':
        if datasetName=='MuHad-Run2012ABCD':
            boxNames = ['MuMu','MuTau','Mu']
        elif datasetName=='ElectronHad-Run2012ABCD':
            boxNames = ['MuEle','EleEle','EleTau','Ele']
        elif datasetName=='HT-HTMHT-Run2012ABCD':
            boxNames = ['TauTauJet','Jet1b','Jet2b','MultiJet']
        elif datasetName=='TTJets':
            boxNames = ['MuEle','MuMu','EleEle','TauTauJet']
        elif datasetName=='SMCocktail':
            boxNames = ['MuTau','Mu','EleTau','Ele','MultiJet','Jet']
        else:
            boxNames = ['MuEle','MuMu','EleEle','EleTau','Ele','MuTau','Mu','TauTauJet','Jet','MultiJet']
    else:
        boxNames = [sys.argv[2]]

    if sys.argv[3]=='All':
        sidebandNames = ['Sideband','FULL']
    else:
        sidebandNames = [sys.argv[3]]

    nToysPerJob = int(nToys/nJobs)
    totalJobs = 0
    nJobsByBox = {}
    for box in boxNames:
        for sideband in sidebandNames:
            resultDir = "toys10k_%s_%s"%(datasetName,fitmode)
            toyDir = resultDir+"/%s_%s"%(sideband,box)
            ffDir = toyDir+"_FF"
            fullSetToys = ["%s/frtoydata_%s_%i.txt"%(toyDir,box,i) for i in xrange(0,nToys)]
            fullSetRoot = ["%s/frtoydata_%s_%i.root"%(toyDir,box,i) for i in xrange(0,nToys)]
            
            allToys = glob.glob("%s/*.txt"%(toyDir))
            allRoot = glob.glob("%s/*.root"%(toyDir))
            doFinalJob = (len(allToys)==nToys and len(allRoot)==nToys)
            
            nJobsByBox[(box,sideband)] = nJobs
            if doFinalJob:
                nJobsByBox[(box,sideband)] = 1
                missingToys = set([])
                missingRoot = set([])
            else:
                missingToys = set(fullSetToys) - set(allToys)
                missingRoot = set(fullSetRoot) - set(allRoot)
                
            if glob.glob("%s/expected_sigbin_%s.root"%(ffDir,box)): doFinalJob = False

            doFinalJob = True
            for t in xrange(0,nJobsByBox[(box,sideband)]):
                
                doToys = False
                doConvertToRoot = False
                for i in xrange(int(t*nToysPerJob),int((t+1)*nToysPerJob)):
                    if "%s/frtoydata_%s_%i.txt"%(toyDir,box,i) in missingToys: doToys = True
                    if "%s/frtoydata_%s_%i.root"%(toyDir,box,i) in missingRoot: doConvertToRoot = True

                if doFinalJob or doToys or doConvertToRoot:
                    outputname,ffDir,pwd = writeBashScript(box,sideband,fitmode,nToys,nToysPerJob,t,doToys,doConvertToRoot,doFinalJob)
                    totalJobs+=1
                    time.sleep(3)
                    os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    #os.system("source "+pwd+"/"+outputname)
                
    print "TOTAL JOBS IS %i"%totalJobs
