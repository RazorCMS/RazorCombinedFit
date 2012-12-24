#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys
from array import *
import time

def writeBashScript(box,sideband,fitmode):
    pwd = os.environ['PWD']
            
    fitResultsDir = "FitResults_%s"%fitmode
    config = "config_summer2012/RazorInclusive2012_%s_btag.config"%fitmode

    submitDir = "submit"
    fitResultMap = {'WJets':'%s/razor_output_WJets_%s_%s.root'%(fitResultsDir,sideband,box),
                    'TTJets':'%s/razor_output_TTJets_%s_%s.root'%(fitResultsDir,sideband,box),
                    'ZJetsToNuNu':'%s/razor_output_ZJetsToNuNu_%s_%s.root'%(fitResultsDir,sideband,box),
                    'SMCocktail':'%s/razor_output_SMCocktail_%s_%s.root'%(fitResultsDir,sideband,box),
                    'MuHad-Run2012AB':'%s/razor_output_MuHad-Run2012AB_%s_%s.root'%(fitResultsDir,sideband,box),
                    'ElectronHad-Run2012AB':'%s/razor_output_ElectronHad-Run2012AB_%s_%s.root'%(fitResultsDir,sideband,box),
                    'HT-HTMHT-Run2012AB':'%s/razor_output_HT-HTMHT-Run2012AB_%s_%s.root'%(fitResultsDir,sideband,box)}
    if box == "TauTauJet" or box=="Jet" or box=="MultiJet":
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
                  'MuHad-Run2012AB':'DATA/MuHad-Run2012AB_%s_BTAG_PF_%s.root'%(label,box),
                  'ElectronHad-Run2012AB':'DATA/ElectronHad-Run2012AB_%s_BTAG_PF_%s.root'%(label,box),
                  'HT-HTMHT-Run2012AB':'DATA/HT-HTMHT-Run2012AB_%s_BTAG_PF_%s.root'%(label,box)}
    resultDir = "toys_%s_%s"%(datasetName,fitmode)
    toyDir = resultDir+"/%s_%s"%(sideband,box)
    ffDir = toyDir+"_FF"

    tagFR = ""
    tag3D = ""

    if sideband == "Sideband":
        tagFR = "--fit-region=LowRsq_LowMR_HighMR"
    if sideband == "FULL":
        tagFR = "--fit-region=LowRsq_LowMR_HighMR"
        
    if fitmode == "3D":
        tag3D = "--3D"
        
    tagPrintPlots = "--printPlots"
        
    os.system("mkdir -p %s"%(submitDir)) 
    # prepare the script to run
    outputname = submitDir+"/submit_"+datasetName+"_"+fitmode+"_"+sideband+"_"+box+".src"
    outputfile = open(outputname,'w')
    outputfile.write('#!/bin/bash\n')
    outputfile.write('cd %s \n'%pwd)
    outputfile.write('echo $PWD \n')
    outputfile.write('eval `scramv1 runtime -sh` \n')
    outputfile.write("mkdir -p %s; mkdir -p %s; mkdir -p %s \n"%(resultDir,toyDir,ffDir))
    #if nToys<1000:
    #    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c %s %s --fit-region %s -i %s --save-toys-from-fit %s -t %i --toy-offset %i -b \n"%(config,datasetMap[datasetName],sideband,fitResultMap[datasetName],toyDir,nToys,0))
    #else:
    #    for t in xrange(0,int(nToys/1000)):
    #        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c %s %s --fit-region %s -i %s --save-toys-from-fit %s -t %i --toy-offset %i -b \n"%(config,datasetMap[datasetName],sideband,fitResultMap[datasetName],toyDir,int(1000), int(t*1000)))
    #    if nToys%1000:
    #        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c %s %s --fit-region %s -i %s --save-toys-from-fit %s -t %i --toy-offset %i -b \n"%(config,datasetMap[datasetName],sideband,fitResultMap[datasetName],toyDir,int(nToys%1000), int(t*1000)))
    #outputfile.write("python scripts/convertToyToROOT.py %s/frtoydata_%s -b \n" %(toyDir, box))
    outputfile.write("rm %s.txt \n" %(toyDir))
    outputfile.write("ls %s/frtoydata_*.root > %s.txt \n" %(toyDir, toyDir))
    outputfile.write("python scripts/expectedYield_sigbin.py 1 %s/expected_sigbin_%s.root %s %s.txt %s %s -b \n"%(ffDir, box, box, toyDir,tagFR,tag3D))
    outputfile.write("python scripts/makeToyPVALUE_sigbin.py %s %s/expected_sigbin_%s.root %s %s %s %s %s -b \n"%(box, ffDir, box, datasetMap[datasetName], ffDir,tagFR,tag3D,tagPrintPlots))
    if datasetName.find("Run") != -1:
        outputfile.write("python scripts/make1DProj.py %s %s/expected_sigbin_%s.root %s %s %s %s %s -b \n"%(box,ffDir,box,fitResultMap[datasetName],ffDir,tagFR,tag3D,tagPrintPlots))
    else:
        outputfile.write("python scripts/make1DProj.py %s %s/expected_sigbin_%s.root %s %s -MC=%s %s %s %s -b \n"%(box,ffDir,box,fitResultMap[datasetName],ffDir,datasetName,tagFR,tag3D,tagPrintPlots))
    
    outputfile.close

    return outputname, ffDir, pwd

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "\nRun the script as follows:\n"
        print "python scripts/runToys DatasetName BoxName FitRegion"
        print "with:"
        print "   DatasetName = name of the sample (TTJets, WJets, SMCocktail, MuHad-Run2012AB, ElectronHad-Run2012AB, etc)"
        print "   BoxName = name of the Box (MuMu, MuEle, etc, or All)"
        print "   FitRegion = name of the fit region (FULL, Sideband, or All)"
        print ""
        print "After the inputs you can specify the following options"
        sys.exit()
    
    datasetName = sys.argv[1]
    #box = sys.argv[2]
    #sideband = sys.argv[3]
    #fitmode = sys.argv[4]
    fitmode = '3D'
    queue = "1nd"
    nToys = 20

    if sys.argv[2]=='All':
        if datasetName=='MuHad-Run2012AB':
            boxNames = ['MuEle','MuMu','MuTau','Mu']
        elif datasetName=='ElectronHad-Run2012AB':
            boxNames = ['EleEle','EleTau','Ele']
        elif datasetName=='HT-HTMHT-Run2012AB':
            boxNames = ['TauTauJet','Jet','MultiJet']
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
    
    for box in boxNames:
        for sideband in sidebandNames:
            
            outputname,ffDir,pwd = writeBashScript(box,sideband,fitmode)
            
            time.sleep(3)
            os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log.log source "+pwd+"/"+outputname)
            os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log.log source "+pwd+"/"+outputname)

            #os.system("source "+pwd+"/"+outputname)
